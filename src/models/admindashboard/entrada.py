from pathlib import Path
import sqlite3
from datetime import datetime
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit,
    QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

# Import robusto: tenta import relativo, senão usa import absoluto
try:
    from .db_utils import _find_db_file, ensure_transacoes_table
except ImportError:
    # Se executado como script direto
    sys.path.insert(0, str(Path(__file__).parent))
    from db_utils import _find_db_file, ensure_transacoes_table


def _ensure_table(db_file):
    # this module no longer manages transacoes_financeiras; keep stub for compatibility
    return


class KumbuDialog(QDialog):
    def __init__(self, parent=None, db_file=None, on_success=None):
        super().__init__(parent)
        self.db_file = db_file
        self.on_success = on_success
        self.setWindowTitle("Adicionar Kumbu")
        self.setGeometry(100, 100, 500, 250)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Data
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Data:"))
        self.date_field = QDateEdit()
        self.date_field.setCalendarPopup(True)
        self.date_field.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_field)
        layout.addLayout(date_layout)

        # Descrição
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Descrição:"))
        self.desc_field = QLineEdit()
        self.desc_field.setPlaceholderText("Ex: Kumbu extra segunda-feira")
        desc_layout.addWidget(self.desc_field)
        layout.addLayout(desc_layout)

        # Valor
        valor_layout = QHBoxLayout()
        valor_layout.addWidget(QLabel("Valor:"))
        self.valor_field = QDoubleSpinBox()
        self.valor_field.setPrefix("AOA ")
        self.valor_field.setDecimals(2)
        self.valor_field.setMaximum(1e12)
        valor_layout.addWidget(self.valor_field)
        layout.addLayout(valor_layout)

        layout.addStretch()

        # Botões no canto inferior
        btn_layout = QHBoxLayout()
        btn_adicionar = QPushButton("Adicionar Kumbu")
        btn_adicionar.clicked.connect(self.add_kumbu)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_adicionar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add_kumbu(self):
        if not self.db_file:
            QMessageBox.warning(self, "Erro", "Arquivo de banco de dados não encontrado.")
            return
        valor = float(self.valor_field.value())
        descricao = self.desc_field.text().strip()
        if valor <= 0:
            QMessageBox.warning(self, "Valor inválido", "Insira um valor maior que zero.")
            return
        if not descricao:
            descricao = "Kumbu"
        data_str = self.date_field.date().toString("yyyy-MM-dd")
        try:
            conn = sqlite3.connect(str(self.db_file))
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO transacoes_financeiras (tipo, descricao, valor, data_transacao) VALUES (?, ?, ?, ?)",
                ("kumbu", descricao, valor, data_str)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sucesso", "Kumbu registrada.")
            if self.on_success:
                self.on_success()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gravar kumbu: {e}")


class EmprestimoDialog(QDialog):
    def __init__(self, parent=None, db_file=None, on_success=None):
        super().__init__(parent)
        self.db_file = db_file
        self.on_success = on_success
        self.setWindowTitle("Registrar Empréstimo")
        self.setGeometry(100, 100, 500, 250)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Data
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Data:"))
        self.date_field = QDateEdit()
        self.date_field.setCalendarPopup(True)
        self.date_field.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_field)
        layout.addLayout(date_layout)

        # Descrição
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Descrição:"))
        self.desc_field = QLineEdit()
        self.desc_field.setPlaceholderText("Ex: Empréstimo pessoal")
        desc_layout.addWidget(self.desc_field)
        layout.addLayout(desc_layout)

        # Valor
        valor_layout = QHBoxLayout()
        valor_layout.addWidget(QLabel("Valor:"))
        self.valor_field = QDoubleSpinBox()
        self.valor_field.setPrefix("AOA ")
        self.valor_field.setDecimals(2)
        self.valor_field.setMaximum(1e12)
        valor_layout.addWidget(self.valor_field)
        layout.addLayout(valor_layout)

        layout.addStretch()

        # Botões no canto inferior
        btn_layout = QHBoxLayout()
        btn_adicionar = QPushButton("Registrar Empréstimo")
        btn_adicionar.clicked.connect(self.add_emprestimo)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_adicionar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add_emprestimo(self):
        if not self.db_file:
            QMessageBox.warning(self, "Erro", "Arquivo de banco de dados não encontrado.")
            return
        valor = float(self.valor_field.value())
        descricao = self.desc_field.text().strip()
        if valor <= 0:
            QMessageBox.warning(self, "Valor inválido", "Insira um valor maior que zero.")
            return
        if not descricao:
            descricao = "Empréstimo"
        data_str = self.date_field.date().toString("yyyy-MM-dd")
        try:
            conn = sqlite3.connect(str(self.db_file))
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO transacoes_financeiras (tipo, descricao, valor, data_transacao) VALUES (?, ?, ?, ?)",
                ("emprestimo", descricao, valor, data_str)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sucesso", "Empréstimo registrado.")
            if self.on_success:
                self.on_success()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gravar empréstimo: {e}")


class EntradaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_file = _find_db_file()
        self._init_ui()
        # ensure transactions table exists so we can record kumbu/emprestimo
        if self.db_file:
            ensure_transacoes_table(self.db_file)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Registrar Entrada")
        title.setStyleSheet("font-weight:700;font-size:16px;")
        layout.addWidget(title)

        # Seletor de mês/ano para análises
        analise_layout = QHBoxLayout()
        lbl_mes = QLabel("Mês:")
        lbl_mes.setAlignment(Qt.AlignVCenter)
        self.mes_picker = QDateEdit()
        self.mes_picker.setDisplayFormat("MMMM yyyy")
        self.mes_picker.setDate(QDate.currentDate())
        self.mes_picker.setCalendarPopup(True)
        btn_calc = QPushButton("Calcular Mês")
        btn_calc.clicked.connect(self.compute_month_stats)
        # calcular automaticamente ao mudar mês
        self.mes_picker.dateChanged.connect(lambda _: self.compute_month_stats())
        btn_atualizar = QPushButton("🔄 Atualizar")
        btn_atualizar.clicked.connect(self.compute_month_stats)
        analise_layout.addWidget(lbl_mes)
        analise_layout.addWidget(self.mes_picker)
        analise_layout.addWidget(btn_calc)
        analise_layout.addWidget(btn_atualizar)
        
        # Botão para Kumbu
        btn_kumbu = QPushButton("Adicionar Kumbu")
        btn_kumbu.clicked.connect(self.open_kumbu_dialog)
        analise_layout.addWidget(btn_kumbu)

        # Botão para Empréstimo
        btn_emprest = QPushButton("Registrar Empréstimo")
        btn_emprest.clicked.connect(self.open_emprestimo_dialog)
        analise_layout.addWidget(btn_emprest)
        analise_layout.addStretch()
        layout.addLayout(analise_layout)
        # Área de resultados do mês: total de vendas, kumbu, empréstimo e ranking de produtos
        results_layout = QVBoxLayout()

        self.total_vendas_label = QLabel("Vendas no mês: AOA 0,00")
        self.kumbu_label = QLabel("Kumbu no mês: AOA 0,00")
        self.emprest_label = QLabel("Empréstimo no mês: AOA 0,00")
        self.total_label = QLabel("Total no mês: AOA 0,00")
        self.total_label.setFont(QFont(None, 12, QFont.Bold))

        results_layout.addWidget(self.total_vendas_label)
        results_layout.addWidget(self.kumbu_label)
        results_layout.addWidget(self.emprest_label)
        results_layout.addWidget(self.total_label)

        # Tabela de produtos vendidos (do mais vendido ao menos vendido)
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(2)
        self.top_table.setHorizontalHeaderLabels(["Produto", "Qtd"])
        self.top_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        results_layout.addWidget(self.top_table)

        layout.addLayout(results_layout)

    def add_transaction(self):
        # transaction creation removed in simplified view
        return

    def open_kumbu_dialog(self):
        dlg = KumbuDialog(self, self.db_file, on_success=self.compute_month_stats)
        dlg.exec_()

    def open_emprestimo_dialog(self):
        dlg = EmprestimoDialog(self, self.db_file, on_success=self.compute_month_stats)
        dlg.exec_()

    def load_transactions(self):
        # removed
        return

    def compute_month_stats(self):
        """Calcula total de vendas no mês selecionado e produtos mais/menos vendidos."""
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

            # Total receita: somar total da tabela vendas no mês
            cur.execute("SELECT SUM(total) as total_mes FROM vendas WHERE strftime('%Y-%m', data_venda) = ?", (ym,))
            r = cur.fetchone()
            total_vendas = r['total_mes'] if r and r['total_mes'] is not None else 0.0
            self.total_vendas_label.setText(f"Vendas no mês: AOA {total_vendas:,.2f}")

            # Somar kumbu e empréstimo do mês
            cur.execute("SELECT SUM(valor) as kumbu_mes FROM transacoes_financeiras WHERE tipo = 'kumbu' AND strftime('%Y-%m', data_transacao) = ?", (ym,))
            r = cur.fetchone()
            kumbu_mes = r['kumbu_mes'] if r and r['kumbu_mes'] is not None else 0.0
            self.kumbu_label.setText(f"Kumbu no mês: AOA {kumbu_mes:,.2f}")

            cur.execute("SELECT SUM(valor) as emprest_mes FROM transacoes_financeiras WHERE tipo = 'emprestimo' AND strftime('%Y-%m', data_transacao) = ?", (ym,))
            r = cur.fetchone()
            emprest_mes = r['emprest_mes'] if r and r['emprest_mes'] is not None else 0.0
            self.emprest_label.setText(f"Empréstimo no mês: AOA {emprest_mes:,.2f}")

            # Total geral = vendas + kumbu + empréstimo
            total_geral = total_vendas + kumbu_mes + emprest_mes
            self.total_label.setText(f"Total no mês: AOA {total_geral:,.2f}")

            # Produtos vendidos (do mais vendido ao menos vendido)
            cur.execute(
                """
                SELECT p.nome_comercial as nome, SUM(iv.quantidade) as qtd
                FROM vendas v
                JOIN itens_venda iv ON iv.venda_id = v.id
                JOIN produtos p ON p.id = iv.produto_id
                WHERE strftime('%Y-%m', v.data_venda) = ?
                GROUP BY p.id
                ORDER BY qtd DESC
                """,
                (ym,)
            )
            top_rows = cur.fetchall()

            conn.close()

            # Popular tabela top (mais -> menos)
            self.top_table.setRowCount(0)
            for r in top_rows:
                row = self.top_table.rowCount()
                self.top_table.insertRow(row)
                self.top_table.setItem(row, 0, QTableWidgetItem(str(r['nome'] or '-')))
                self.top_table.setItem(row, 1, QTableWidgetItem(str(int(r['qtd'] or 0))))

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Falha ao calcular estatísticas: {e}")
