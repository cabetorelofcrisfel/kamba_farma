from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` and other top-level packages are importable
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.paths import DB_DIR
from database.db import get_db_path, connect


class ProdutosRegistradosView(QWidget):
    """View para exibir produtos já registrados em forma de tabela.

    Exibe: Foto, Nome Comercial, Princípio Ativo, Categoria, Forma Farmacêutica,
    Preço Venda, Preço Compra, Código Barras, Unidade, Stock, Stock Mínimo,
    Fornecedor, Lote, Ativo, Criado Em
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_products()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(" Produtos Registrados")
        title.setStyleSheet("font-weight:700;font-size:16px;padding:6px 0;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(15)
        self.table.setHorizontalHeaderLabels([
            "Foto", "Nome Comercial", "Princípio Ativo", "Categoria", "Forma Farmacêutica",
            "Preço Venda", "Preço Compra", "Código Barras", "Unidade", "Stock",
            "Stock Mínimo", "Fornecedor", "Lote", "Ativo", "Criado Em"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(80)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.table)

    def load_products(self):
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "SELECT p.*, f.nome as fornecedor_nome, l.numero_lote as lote_numero "
                "FROM produtos p "
                "LEFT JOIN fornecedores f ON p.fornecedor_padrao_id = f.id "
                "LEFT JOIN lotes l ON p.lote_padrao_id = l.id "
                "ORDER BY p.nome_comercial"
            )
            rows = cur.fetchall()
            conn.close()

            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                # Foto
                photo = r['foto'] if 'foto' in r.keys() else None
                if photo:
                    pix = QPixmap()
                    pix.loadFromData(photo)
                    if not pix.isNull():
                        pix = pix.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        lbl = QLabel()
                        lbl.setPixmap(pix)
                        lbl.setAlignment(Qt.AlignCenter)
                        self.table.setCellWidget(i, 0, lbl)
                    else:
                        self.table.setItem(i, 0, QTableWidgetItem(""))
                else:
                    self.table.setItem(i, 0, QTableWidgetItem(""))

                def safe_get(key):
                    return r[key] if key in r.keys() else None

                self.table.setItem(i, 1, QTableWidgetItem(safe_get('nome_comercial') or ''))
                self.table.setItem(i, 2, QTableWidgetItem(safe_get('principio_ativo') or ''))
                self.table.setItem(i, 3, QTableWidgetItem(safe_get('categoria') or ''))
                self.table.setItem(i, 4, QTableWidgetItem(safe_get('forma_farmaceutica') or ''))
                self.table.setItem(i, 5, QTableWidgetItem(f"{(safe_get('preco_venda') or 0):.2f}"))
                self.table.setItem(i, 6, QTableWidgetItem(f"{(safe_get('preco_compra') or 0):.2f}"))
                self.table.setItem(i, 7, QTableWidgetItem(safe_get('codigo_barras') or ''))
                self.table.setItem(i, 8, QTableWidgetItem(safe_get('unidade') or ''))
                self.table.setItem(i, 9, QTableWidgetItem(str(safe_get('stock') or 0)))
                self.table.setItem(i, 10, QTableWidgetItem(str(safe_get('stock_minimo') or 0)))
                self.table.setItem(i, 11, QTableWidgetItem(safe_get('fornecedor_nome') or ''))
                self.table.setItem(i, 12, QTableWidgetItem(safe_get('lote_numero') or ''))
                self.table.setItem(i, 13, QTableWidgetItem(str(safe_get('ativo') or '')))
                self.table.setItem(i, 14, QTableWidgetItem(str(safe_get('criado_em') or '')))

        except Exception as e:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Erro"])
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Erro ao carregar produtos: {e}"))
