from pathlib import Path
import sqlite3
from datetime import datetime
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

# Import robusto: tenta import relativo, senão usa import absoluto
try:
    from .db_utils import _find_db_file
except ImportError:
    # Se executado como script direto
    sys.path.insert(0, str(Path(__file__).parent))
    from db_utils import _find_db_file


def _find_db_file():
    root = Path(__file__).resolve()
    for _ in range(8):
        db_dir = root / "database"
        if db_dir.exists():
            db_file = db_dir / "kamba_farma.db"
            return db_file if db_file.exists() else None
        root = root.parent
    return None


class DiarioView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_file = _find_db_file()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Registro Diário")
        title.setStyleSheet("font-weight:700;font-size:16px;")
        layout.addWidget(title)

        # Seletor de data
        date_layout = QHBoxLayout()
        lbl_data = QLabel("Data:")
        lbl_data.setAlignment(Qt.AlignVCenter)
        self.data_picker = QDateEdit()
        self.data_picker.setDisplayFormat("dd/MM/yyyy")
        self.data_picker.setDate(QDate.currentDate())
        self.data_picker.setCalendarPopup(True)
        # Recalcular ao mudar data
        self.data_picker.dateChanged.connect(self.load_daily_report)
        btn_atualizar = QPushButton("🔄 Atualizar")
        btn_atualizar.clicked.connect(self.load_daily_report)
        date_layout.addWidget(lbl_data)
        date_layout.addWidget(self.data_picker)
        date_layout.addWidget(btn_atualizar)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Resumo do dia
        resumo_layout = QVBoxLayout()

        self.vendas_label = QLabel("Total de Vendas: AOA 0,00")
        self.vendas_label.setFont(QFont(None, 12, QFont.Bold))
        resumo_layout.addWidget(self.vendas_label)

        self.saidas_label = QLabel("Total de Saídas: AOA 0,00")
        self.saidas_label.setFont(QFont(None, 11))
        resumo_layout.addWidget(self.saidas_label)

        self.saldo_label = QLabel("Saldo do Dia: AOA 0,00")
        self.saldo_label.setFont(QFont(None, 12, QFont.Bold))
        resumo_layout.addWidget(self.saldo_label)

        layout.addLayout(resumo_layout)

        # Tabela de produtos vendidos
        lbl_produtos = QLabel("Produtos Vendidos:")
        lbl_produtos.setStyleSheet("font-weight:700;")
        layout.addWidget(lbl_produtos)

        self.produtos_table = QTableWidget()
        self.produtos_table.setColumnCount(3)
        self.produtos_table.setHorizontalHeaderLabels(["Produto", "Quantidade", "Valor Total"])
        self.produtos_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.produtos_table)

        # Tabela de saídas
        lbl_saidas = QLabel("Saídas do Dia:")
        lbl_saidas.setStyleSheet("font-weight:700;")
        layout.addWidget(lbl_saidas)

        self.saidas_table = QTableWidget()
        self.saidas_table.setColumnCount(2)
        self.saidas_table.setHorizontalHeaderLabels(["Descrição", "Valor"])
        self.saidas_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.saidas_table)

        # Carregar dados do dia atual
        self.load_daily_report()

    def load_daily_report(self):
        """Carrega o relatório diário: vendas, saídas e produtos."""
        if not self.db_file:
            QMessageBox.warning(self, "Erro", "Arquivo de banco de dados não encontrado.")
            return

        data = self.data_picker.date()
        data_str = data.toString("yyyy-MM-dd")

        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Total de vendas do dia
            cur.execute(
                "SELECT SUM(total) as total_vendas FROM vendas WHERE DATE(data_venda) = ?",
                (data_str,)
            )
            r = cur.fetchone()
            total_vendas = r['total_vendas'] if r and r['total_vendas'] is not None else 0.0
            self.vendas_label.setText(f"Total de Vendas: AOA {total_vendas:,.2f}")

            # Total de saídas do dia
            cur.execute(
                "SELECT SUM(valor) as total_saidas FROM transacoes_financeiras WHERE tipo = 'saida' AND DATE(data_transacao) = ?",
                (data_str,)
            )
            r = cur.fetchone()
            total_saidas = r['total_saidas'] if r and r['total_saidas'] is not None else 0.0
            self.saidas_label.setText(f"Total de Saídas: AOA {total_saidas:,.2f}")

            # Saldo = vendas - saídas
            saldo = total_vendas - total_saidas
            self.saldo_label.setText(f"Saldo do Dia: AOA {saldo:,.2f}")

            # Produtos vendidos no dia
            cur.execute(
                """
                SELECT p.nome_comercial as nome, SUM(iv.quantidade) as qtd, SUM(iv.subtotal) as subtotal
                FROM vendas v
                JOIN itens_venda iv ON iv.venda_id = v.id
                JOIN produtos p ON p.id = iv.produto_id
                WHERE DATE(v.data_venda) = ?
                GROUP BY p.id
                ORDER BY qtd DESC
                """,
                (data_str,)
            )
            produtos_rows = cur.fetchall()

            # Preencher tabela de produtos
            self.produtos_table.setRowCount(0)
            for r in produtos_rows:
                row = self.produtos_table.rowCount()
                self.produtos_table.insertRow(row)
                self.produtos_table.setItem(row, 0, QTableWidgetItem(str(r['nome'] or '-')))
                self.produtos_table.setItem(row, 1, QTableWidgetItem(str(int(r['qtd'] or 0))))
                self.produtos_table.setItem(row, 2, QTableWidgetItem(f"AOA {r['subtotal']:,.2f}" if r['subtotal'] else "AOA 0,00"))

            # Saídas do dia
            cur.execute(
                "SELECT descricao, valor FROM transacoes_financeiras WHERE tipo = 'saida' AND DATE(data_transacao) = ? ORDER BY data_transacao DESC",
                (data_str,)
            )
            saidas_rows = cur.fetchall()

            # Preencher tabela de saídas
            self.saidas_table.setRowCount(0)
            for r in saidas_rows:
                row = self.saidas_table.rowCount()
                self.saidas_table.insertRow(row)
                self.saidas_table.setItem(row, 0, QTableWidgetItem(str(r['descricao'] or '')))
                self.saidas_table.setItem(row, 1, QTableWidgetItem(f"AOA {r['valor']:,.2f}"))

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Falha ao carregar relatório diário: {e}")
