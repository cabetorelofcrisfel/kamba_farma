from pathlib import Path
import sqlite3
from datetime import datetime
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

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


class BalancoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_file = _find_db_file()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Balanço Final")
        title.setStyleSheet("font-weight:700;font-size:16px;")
        layout.addWidget(title)

        # Seletor de mês
        mes_layout = QHBoxLayout()
        lbl_mes = QLabel("Mês:")
        lbl_mes.setAlignment(Qt.AlignVCenter)
        self.mes_picker = QDateEdit()
        self.mes_picker.setDisplayFormat("MMMM yyyy")
        self.mes_picker.setDate(QDate.currentDate())
        self.mes_picker.setCalendarPopup(True)
        self.mes_picker.dateChanged.connect(self.compute_balanco)
        btn_atualizar = QPushButton(" Atualizar")
        btn_atualizar.clicked.connect(self.compute_balanco)
        mes_layout.addWidget(lbl_mes)
        mes_layout.addWidget(self.mes_picker)
        mes_layout.addWidget(btn_atualizar)
        mes_layout.addStretch()
        layout.addLayout(mes_layout)

        # ===== SEÇÃO DE ENTRADAS =====
        entrada_label = QLabel(" ENTRADAS")
        entrada_label.setStyleSheet("font-weight:700;font-size:12px;color:#009688;margin-top:10px;")
        layout.addWidget(entrada_label)

        # Subtotais de entradas
        self.vendas_label = QLabel("Vendas: AOA 0,00")
        self.kumbu_label = QLabel("Kumbu: AOA 0,00")
        self.emprestimo_label = QLabel("Empréstimo: AOA 0,00")
        self.total_entrada_label = QLabel("Total Entradas: AOA 0,00")
        self.total_entrada_label.setFont(QFont(None, 11, QFont.Bold))
        self.total_entrada_label.setStyleSheet("color:#009688;")

        layout.addWidget(self.vendas_label)
        layout.addWidget(self.kumbu_label)
        layout.addWidget(self.emprestimo_label)
        layout.addWidget(self.total_entrada_label)

        # ===== SEÇÃO DE SAÍDAS =====
        saida_label = QLabel(" SAÍDAS")
        saida_label.setStyleSheet("font-weight:700;font-size:12px;color:#FF6B6B;margin-top:15px;")
        layout.addWidget(saida_label)

        # Subtotais de saídas por categoria
        self.transferencia_label = QLabel("Transferência: AOA 0,00")
        self.stock_label = QLabel("Compra Stock: AOA 0,00")
        self.pessoal_label = QLabel("Uso Pessoal: AOA 0,00")
        self.passagem_label = QLabel("Passagem: AOA 0,00")
        self.salario_label = QLabel("Salário: AOA 0,00")
        self.outro_label = QLabel("Outro: AOA 0,00")
        self.total_saida_label = QLabel("Total Saídas: AOA 0,00")
        self.total_saida_label.setFont(QFont(None, 11, QFont.Bold))
        self.total_saida_label.setStyleSheet("color:#FF6B6B;")

        layout.addWidget(self.transferencia_label)
        layout.addWidget(self.stock_label)
        layout.addWidget(self.pessoal_label)
        layout.addWidget(self.passagem_label)
        layout.addWidget(self.salario_label)
        layout.addWidget(self.outro_label)
        layout.addWidget(self.total_saida_label)

        # ===== RESULTADO FINAL =====
        resultado_label = QLabel(" RESULTADO")
        resultado_label.setStyleSheet("font-weight:700;font-size:12px;margin-top:15px;")
        layout.addWidget(resultado_label)

        self.lucro_label = QLabel("Lucro/Prejuízo: AOA 0,00")
        self.lucro_label.setFont(QFont(None, 14, QFont.Bold))
        layout.addWidget(self.lucro_label)

        layout.addStretch()

        # Carregar balanço do mês atual
        self.compute_balanco()

    def compute_balanco(self):
        """Calcula o balanço completo do mês: entradas, saídas e resultado."""
        if not self.db_file:
            QMessageBox.warning(self, "Erro", "Arquivo de banco de dados não encontrado.")
            return

        date = self.mes_picker.date()
        year = date.year()
        month = date.month()
        ym = f"{year}-{month:02d}"

        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # ===== ENTRADAS =====
            # Vendas
            cur.execute("SELECT SUM(total) as total_vendas FROM vendas WHERE strftime('%Y-%m', data_venda) = ?", (ym,))
            r = cur.fetchone()
            total_vendas = r['total_vendas'] if r and r['total_vendas'] is not None else 0.0
            self.vendas_label.setText(f"Vendas: AOA {total_vendas:,.2f}")

            # Kumbu
            cur.execute("SELECT SUM(valor) as total_kumbu FROM transacoes_financeiras WHERE tipo = 'kumbu' AND strftime('%Y-%m', data_transacao) = ?", (ym,))
            r = cur.fetchone()
            total_kumbu = r['total_kumbu'] if r and r['total_kumbu'] is not None else 0.0
            self.kumbu_label.setText(f"Kumbu: AOA {total_kumbu:,.2f}")

            # Empréstimo
            cur.execute("SELECT SUM(valor) as total_emprest FROM transacoes_financeiras WHERE tipo = 'emprestimo' AND strftime('%Y-%m', data_transacao) = ?", (ym,))
            r = cur.fetchone()
            total_emprest = r['total_emprest'] if r and r['total_emprest'] is not None else 0.0
            self.emprestimo_label.setText(f"Empréstimo: AOA {total_emprest:,.2f}")

            # Total de entradas
            total_entrada = total_vendas + total_kumbu + total_emprest
            self.total_entrada_label.setText(f"Total Entradas: AOA {total_entrada:,.2f}")

            # ===== SAÍDAS =====
            categorias = [
                ("Transferência", self.transferencia_label),
                ("Compra Stock", self.stock_label),
                ("Uso Pessoal", self.pessoal_label),
                ("Passagem", self.passagem_label),
                ("Salário", self.salario_label),
                ("Outro", self.outro_label)
            ]

            total_saida = 0.0
            for cat_name, label_widget in categorias:
                cur.execute(
                    "SELECT SUM(valor) as cat_total FROM transacoes_financeiras WHERE tipo = 'saida' AND descricao LIKE ? AND strftime('%Y-%m', data_transacao) = ?",
                    (f"{cat_name}:%", ym)
                )
                r = cur.fetchone()
                cat_total = r['cat_total'] if r and r['cat_total'] is not None else 0.0
                total_saida += cat_total
                label_widget.setText(f"{cat_name}: AOA {cat_total:,.2f}")

            self.total_saida_label.setText(f"Total Saídas: AOA {total_saida:,.2f}")

            # ===== RESULTADO FINAL =====
            lucro = total_entrada - total_saida
            self.lucro_label.setText(f"Lucro/Prejuízo: AOA {lucro:,.2f}")
            
            # Colorir resultado (verde = lucro, vermelho = prejuízo)
            if lucro >= 0:
                self.lucro_label.setStyleSheet("color:#27AE60;font-weight:bold;font-size:14px;")
            else:
                self.lucro_label.setStyleSheet("color:#E74C3C;font-weight:bold;font-size:14px;")

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Falha ao calcular balanço: {e}")
