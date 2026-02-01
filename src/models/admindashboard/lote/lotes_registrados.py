from pathlib import Path
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.paths import DB_DIR
from database.db import connect, get_db_path


class LotesRegistradosView(QWidget):
    """View para exibir lotes já registrados com ações básicas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.load_lotes()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("📋 Lotes Registrados")
        header.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Produto", "Lote", "Validade", "Quantidade", "Preço Compra", "Fornecedor", "Data Entrada", "Ações"
        ])
        header_h = self.table.horizontalHeader()
        header_h.setSectionResizeMode(QHeaderView.Interactive)
        header_h.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        # Esconder coluna ID para que o usuário não veja o identificador interno
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)

        btns = QHBoxLayout()
        refresh = QPushButton("🔄 Atualizar")
        refresh.clicked.connect(self.load_lotes)
        btns.addStretch()
        btns.addWidget(refresh)
        layout.addLayout(btns)

    def load_lotes(self):
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT l.id, l.numero_lote, l.validade, l.quantidade_atual, l.preco_compra, l.data_entrada,
                       p.nome_comercial AS produto_nome, f.nome AS fornecedor_nome
                FROM lotes l
                LEFT JOIN produtos p ON l.produto_id = p.id
                LEFT JOIN fornecedores f ON l.fornecedor_id = f.id
                WHERE l.ativo = 1
                ORDER BY l.data_entrada DESC
            """)
            rows = cur.fetchall()
            conn.close()

            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table.setItem(i, 0, QTableWidgetItem(str(r['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(r['produto_nome'] or "-"))
                self.table.setItem(i, 2, QTableWidgetItem(r['numero_lote'] or "-"))
                self.table.setItem(i, 3, QTableWidgetItem(str(r['validade'] or "-")))
                self.table.setItem(i, 4, QTableWidgetItem(str(r['quantidade_atual'] or 0)))
                self.table.setItem(i, 5, QTableWidgetItem(str(r['preco_compra'] or 0.0)))
                self.table.setItem(i, 6, QTableWidgetItem(r['fornecedor_nome'] or "-"))
                self.table.setItem(i, 7, QTableWidgetItem(str(r['data_entrada'] or "-")))

                # Actions: Deactivate
                btn = QPushButton("Desativar")
                btn.setProperty('lote_id', r['id'])
                btn.clicked.connect(lambda _, lid=r['id']: self._on_deactivate(lid))
                self.table.setCellWidget(i, 8, btn)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar lotes: {e}")

    def _on_deactivate(self, lote_id: int):
        mb = QMessageBox.question(self, "Confirmar", "Deseja desativar este lote?", QMessageBox.Yes | QMessageBox.No)
        if mb != QMessageBox.Yes:
            return
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute("UPDATE lotes SET ativo=0 WHERE id=?", (lote_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sucesso", "Lote desativado.")
            self.load_lotes()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao desativar lote: {e}")
