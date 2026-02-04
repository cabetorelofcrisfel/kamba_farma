from pathlib import Path
import sqlite3
from typing import List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


def _find_db_path() -> Path:
    p = Path(__file__).resolve()
    for _ in range(8):
        candidate = p.parent / "database" / "kamba_farma.db"
        if candidate.exists():
            return candidate
        p = p.parent
    # fallback to repository database path
    return Path(__file__).resolve().parents[3] / "database" / "kamba_farma.db"


class ManageHighlightPage(QWidget):
    """View que mostra os produtos em destaque (mais vendidos)."""

    def __init__(self, parent=None, limit: int = 10):
        super().__init__(parent)
        self.limit = limit
        self._setup_ui()
        self.load_top_products()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        title = QLabel(" Produtos em Destaque")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2C3E50;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["#", "Produto", "Vendidos"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def _get_conn(self):
        db_path = _find_db_path()
        return sqlite3.connect(str(db_path))

    def load_top_products(self):
        """Busca os produtos mais vendidos e popula a tabela."""
        try:
            conn = self._get_conn()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            cur.execute(
                """
                SELECT p.id, p.nome, COALESCE(SUM(iv.quantidade), 0) AS total_vendido
                FROM produtos p
                LEFT JOIN itens_venda iv ON iv.produto_id = p.id
                GROUP BY p.id
                ORDER BY total_vendido DESC
                LIMIT ?
                """,
                (self.limit,)
            )

            rows: List[sqlite3.Row] = cur.fetchall()
            self.table.setRowCount(len(rows))

            for i, r in enumerate(rows):
                rank_item = QTableWidgetItem(str(i + 1))
                name_item = QTableWidgetItem(r["nome"] if "nome" in r.keys() else str(r[1]))
                sold_item = QTableWidgetItem(str(r["total_vendido"]))

                rank_item.setTextAlignment(Qt.AlignCenter)
                sold_item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(i, 0, rank_item)
                self.table.setItem(i, 1, name_item)
                self.table.setItem(i, 2, sold_item)

            self.table.resizeColumnsToContents()
        except Exception as e:
            # If DB not available, show a friendly message row
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("-"))
            self.table.setItem(0, 1, QTableWidgetItem("Banco de dados indisponível"))
            self.table.setItem(0, 2, QTableWidgetItem("0"))
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    # Quick local check (non-GUI safe): import and instantiate class
    p = ManageHighlightPage()
    print("ManageHighlightPage OK")
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ManageHighlightPage(QWidget):
    """Placeholder para gerir destaques/produtos em promoção."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("⭐ Gerir Destaques\n(Implementar seleção de destaque e prioridade)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
