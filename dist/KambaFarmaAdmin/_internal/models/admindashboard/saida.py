from pathlib import Path
import sqlite3
from datetime import datetime
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit,
    QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QComboBox
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
    conn = sqlite3.connect(str(db_file))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transacoes_financeiras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL,
            data_transacao TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


class SaidaDialog(QDialog):
    """Dialog genérico para registrar saídas com categoria selecionável"""
    def __init__(self, parent=None, db_file=None, on_success=None):
        super().__init__(parent)
        self.db_file = db_file
        self.on_success = on_success
        self.setWindowTitle("Registrar Saída")
        self.setGeometry(100, 100, 550, 300)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Categoria
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Categoria:"))
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems([
            "Transferência",
            "Compra Stock",
            "Uso Pessoal",
            "Passagem",
            "Salário",
            "Outro"
        ])
        cat_layout.addWidget(self.categoria_combo)
        layout.addLayout(cat_layout)

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
        self.desc_field.setPlaceholderText("Ex: Pagamento para fornecedor XYZ")
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
        btn_adicionar = QPushButton("Registrar Saída")
        btn_adicionar.clicked.connect(self.add_saida)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_adicionar)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add_saida(self):
        if not self.db_file:
            QMessageBox.warning(self, "Erro", "Arquivo de banco de dados não encontrado.")
            return
        valor = float(self.valor_field.value())
        descricao = self.desc_field.text().strip()
        categoria = self.categoria_combo.currentText()
        
        if valor <= 0:
            QMessageBox.warning(self, "Valor inválido", "Insira um valor maior que zero.")
            return
        if not descricao:
            descricao = categoria
        
        data_str = self.date_field.date().toString("yyyy-MM-dd")
        
        try:
            conn = sqlite3.connect(str(self.db_file))
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO transacoes_financeiras (tipo, descricao, valor, data_transacao) VALUES (?, ?, ?, ?)",
                ("saida", f"{categoria}: {descricao}", valor, data_str)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sucesso", "Saída registrada.")
            if self.on_success:
                self.on_success()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gravar saída: {e}")


class SaidaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_file = _find_db_file()
        self._init_ui()
        # ensure transactions table exists so we can record saidas
        if self.db_file:
            _ensure_table(self.db_file)

    def _init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Registrar Saída")
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
        btn_atualizar = QPushButton(" Atualizar")
        btn_atualizar.clicked.connect(self.compute_month_stats)
        analise_layout.addWidget(lbl_mes)
        analise_layout.addWidget(self.mes_picker)
        analise_layout.addWidget(btn_calc)
        analise_layout.addWidget(btn_atualizar)
        
        # Botões para categorias de saída
        btn_transferencia = QPushButton("Transferência")
        btn_transferencia.clicked.connect(lambda: self.open_saida_dialog("Transferência"))
        analise_layout.addWidget(btn_transferencia)

        btn_stock = QPushButton("Compra Stock")
        btn_stock.clicked.connect(lambda: self.open_saida_dialog("Compra Stock"))
        analise_layout.addWidget(btn_stock)

        btn_pessoal = QPushButton("Uso Pessoal")
        btn_pessoal.clicked.connect(lambda: self.open_saida_dialog("Uso Pessoal"))
        analise_layout.addWidget(btn_pessoal)

        btn_passagem = QPushButton("Passagem")
        btn_passagem.clicked.connect(lambda: self.open_saida_dialog("Passagem"))
        analise_layout.addWidget(btn_passagem)

        btn_salario = QPushButton("Salário")
        btn_salario.clicked.connect(lambda: self.open_saida_dialog("Salário"))
        analise_layout.addWidget(btn_salario)

        btn_outro = QPushButton("Outro")
        btn_outro.clicked.connect(lambda: self.open_saida_dialog("Outro"))
        analise_layout.addWidget(btn_outro)
        
        analise_layout.addStretch()
        layout.addLayout(analise_layout)

        # Área de resultados do mês: totais por categoria e total geral
        results_layout = QVBoxLayout()

        self.total_label = QLabel("Total saído no mês: AOA 0,00")
        self.total_label.setFont(QFont(None, 12, QFont.Bold))
        results_layout.addWidget(self.total_label)

        # Subtotais por categoria
        self.transferencia_label = QLabel("Transferência: AOA 0,00")
        self.stock_label = QLabel("Compra Stock: AOA 0,00")
        self.pessoal_label = QLabel("Uso Pessoal: AOA 0,00")
        self.passagem_label = QLabel("Passagem: AOA 0,00")
        self.salario_label = QLabel("Salário: AOA 0,00")
        self.outro_label = QLabel("Outro: AOA 0,00")

        results_layout.addWidget(self.transferencia_label)
        results_layout.addWidget(self.stock_label)
        results_layout.addWidget(self.pessoal_label)
        results_layout.addWidget(self.passagem_label)
        results_layout.addWidget(self.salario_label)
        results_layout.addWidget(self.outro_label)

        # Tabela de saídas registradas
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Data", "Descrição", "Valor"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        results_layout.addWidget(self.table)

        layout.addLayout(results_layout)

    def open_saida_dialog(self, categoria=None):
        dlg = SaidaDialog(self, self.db_file, on_success=self.compute_month_stats)
        if categoria:
            # Pre-seleciona a categoria se foi passada
            idx = dlg.categoria_combo.findText(categoria)
            if idx >= 0:
                dlg.categoria_combo.setCurrentIndex(idx)
        dlg.exec_()

    def compute_month_stats(self):
        """Calcula total de saídas no mês selecionado, por categoria."""
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

            # Total geral de saídas
            cur.execute("SELECT SUM(valor) as total_saida FROM transacoes_financeiras WHERE tipo = 'saida' AND strftime('%Y-%m', data_transacao) = ?", (ym,))
            r = cur.fetchone()
            total_saida = r['total_saida'] if r and r['total_saida'] is not None else 0.0
            self.total_label.setText(f"Total saído no mês: AOA {total_saida:,.2f}")

            # Totais por categoria (procura pela descrição que começa com a categoria)
            categorias = [
                ("Transferência", self.transferencia_label),
                ("Compra Stock", self.stock_label),
                ("Uso Pessoal", self.pessoal_label),
                ("Passagem", self.passagem_label),
                ("Salário", self.salario_label),
                ("Outro", self.outro_label)
            ]

            for cat_name, label_widget in categorias:
                cur.execute(
                    "SELECT SUM(valor) as cat_total FROM transacoes_financeiras WHERE tipo = 'saida' AND descricao LIKE ? AND strftime('%Y-%m', data_transacao) = ?",
                    (f"{cat_name}:%", ym)
                )
                r = cur.fetchone()
                cat_total = r['cat_total'] if r and r['cat_total'] is not None else 0.0
                label_widget.setText(f"{cat_name}: AOA {cat_total:,.2f}")

            # Carregar tabela de saídas
            cur.execute("SELECT data_transacao, descricao, valor FROM transacoes_financeiras WHERE tipo = 'saida' AND strftime('%Y-%m', data_transacao) = ? ORDER BY data_transacao DESC LIMIT 100", (ym,))
            rows = cur.fetchall()
            
            self.table.setRowCount(0)
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r['data_transacao'])))
                self.table.setItem(row, 1, QTableWidgetItem(str(r['descricao'] or '')))
                self.table.setItem(row, 2, QTableWidgetItem(f"AOA {r['valor']:,.2f}"))

            conn.close()

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Falha ao calcular estatísticas: {e}")

    def add_transaction(self):
        if not self.db_file:
            QMessageBox.warning(self, "Erro", "Arquivo de banco de dados não encontrado.")
            return
        descricao = self.desc.text().strip()
        valor = float(self.valor.value())
        data_str = self.date.date().toString("yyyy-MM-dd")
        if valor <= 0:
            QMessageBox.warning(self, "Valor inválido", "Insira um valor maior que zero.")
            return
        try:
            conn = sqlite3.connect(str(self.db_file))
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO transacoes_financeiras (tipo, descricao, valor, data_transacao) VALUES (?, ?, ?, ?)",
                ("saida", descricao, valor, data_str)
            )
            conn.commit()
            conn.close()
            self.desc.clear()
            self.valor.setValue(0)
            self.load_transactions()
            QMessageBox.information(self, "Sucesso", "Saída registrada.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gravar saída: {e}")

    def load_transactions(self):
        self.table.setRowCount(0)
        if not self.db_file:
            return
        try:
            conn = sqlite3.connect(str(self.db_file))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT data_transacao, descricao, valor FROM transacoes_financeiras WHERE tipo = 'saida' ORDER BY data_transacao DESC LIMIT 200")
            rows = cur.fetchall()
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r['data_transacao'])))
                self.table.setItem(row, 1, QTableWidgetItem(str(r['descricao'] or '')))
                self.table.setItem(row, 2, QTableWidgetItem(f"AOA {r['valor']:,.2f}"))
            conn.close()
        except Exception:
            pass
