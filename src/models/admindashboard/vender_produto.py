from pathlib import Path
import sys
import sqlite3
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QMessageBox, QScrollArea, QGridLayout,
    QSizePolicy, QSpacerItem, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter, QPainterPath, QIcon, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from datetime import datetime

from colors import *

class RoundedFrame(QFrame):
    """Frame com cantos arredondados."""
    def __init__(self, radius=12, parent=None):
        super().__init__(parent)
        self.radius = radius
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        
        painter.fillRect(self.rect(), QColor(CARD_BG))
        painter.setPen(QColor(BORDER_COLOR))
        painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, self.radius, self.radius)


class ProductCard(QFrame):
    """Card para exibir informações do produto."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(180)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Container da imagem
        self.image_container = QFrame()
        self.image_container.setFixedSize(140, 140)
        self.image_container.setStyleSheet(f"""
            QFrame {{
                background-color: #F9FAFB;
                border-radius: 8px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_layout.setContentsMargins(10, 10, 10, 10)
        
        self.product_image = QLabel()
        self.product_image.setAlignment(Qt.AlignCenter)
        self.product_image.setFixedSize(120, 120)
        self.product_image.setText("")
        self.product_image.setStyleSheet("font-size: 48px; color: #9CA3AF;")
        
        self.image_layout.addWidget(self.product_image)
        
        # Informações do produto
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(12)
        
        # Nome do produto
        self.name_label = QLabel("Nenhum produto selecionado")
        self.name_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        """)
        self.name_label.setWordWrap(True)
        
        # Detalhes
        details_frame = QFrame()
        details_layout = QGridLayout(details_frame)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setVerticalSpacing(8)
        details_layout.setHorizontalSpacing(20)
        
        # Stock
        self.stock_label = QLabel("Estoque: --")
        self.stock_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        
        # Preço
        self.price_label = QLabel("Preço: --")
        self.price_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        
        # Código
        self.code_label = QLabel("Código: --")
        self.code_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        
        # Categoria
        self.category_label = QLabel("Categoria: --")
        self.category_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        
        details_layout.addWidget(self.stock_label, 0, 0)
        details_layout.addWidget(self.price_label, 0, 1)
        details_layout.addWidget(self.code_label, 1, 0)
        details_layout.addWidget(self.category_label, 1, 1)
        
        # Quantidade a comprar
        quantity_frame = QFrame()
        quantity_layout = QHBoxLayout(quantity_frame)
        quantity_layout.setContentsMargins(0, 0, 0, 0)
        quantity_layout.setSpacing(10)
        
        quantity_label = QLabel("Quantidade:")
        quantity_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY};")
        
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 1000)
        self.quantity_spinbox.setValue(1)
        self.quantity_spinbox.setFixedWidth(100)
        self.quantity_spinbox.setStyleSheet(f"""
            QSpinBox {{
                padding: 8px 12px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 6px;
                font-size: 14px;
            }}
            QSpinBox:focus {{
                border-color: {PRIMARY_COLOR};
            }}
        """)
        
        self.add_to_cart_btn = QPushButton(" Adicionar à Venda")
        self.add_to_cart_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #3B52CC;
            }}
            QPushButton:disabled {{
                background-color: {TEXT_LIGHT};
                cursor: not-allowed;
            }}
        """)
        self.add_to_cart_btn.setCursor(Qt.PointingHandCursor)
        self.add_to_cart_btn.setEnabled(False)
        
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_spinbox)
        quantity_layout.addStretch()
        quantity_layout.addWidget(self.add_to_cart_btn)
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(details_frame)
        info_layout.addStretch()
        info_layout.addWidget(quantity_frame)
        
        layout.addWidget(self.image_container)
        layout.addWidget(info_frame, 1)
    
    def set_product_info(self, name, stock, price, code, category, image_bytes=None):
        """Define as informações do produto no card."""
        self.name_label.setText(name)
        self.stock_label.setText(f"Estoque: {stock}")
        self.price_label.setText(f"Preço: Kz {price:,.2f}")
        self.code_label.setText(f"Código: {code}" if code else "Código: --")
        self.category_label.setText(f"Categoria: {category}" if category else "Categoria: --")
        
        if image_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(image_bytes):
                pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.product_image.setPixmap(pixmap)
            else:
                self.product_image.setText("")
                self.product_image.setStyleSheet("font-size: 48px; color: #9CA3AF;")
        else:
            self.product_image.setText("")
            self.product_image.setStyleSheet("font-size: 48px; color: #9CA3AF;")
        
        # Atualizar quantidade máxima baseada no estoque
        self.quantity_spinbox.setMaximum(stock)
        self.quantity_spinbox.setValue(1)
        
        # Habilitar botão
        self.add_to_cart_btn.setEnabled(stock > 0)
        
        # Mudar cor do estoque se estiver baixo
        if stock <= 5:
            self.stock_label.setStyleSheet(f"color: {WARNING_COLOR}; font-weight: 600; font-size: 14px;")
        elif stock == 0:
            self.stock_label.setStyleSheet(f"color: {DANGER_COLOR}; font-weight: 600; font-size: 14px;")
        else:
            self.stock_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")


class SaleItemTable(QTableWidget):
    """Tabela para exibir itens da venda."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Produto", "Quantidade", "Preço Unit.", "Subtotal", "Ações", "Remover"])
        
        # Configurar cabeçalho
        header = self.horizontalHeader()
        header.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: #F9FAFB;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid {BORDER_COLOR};
                font-weight: 600;
                color: {TEXT_PRIMARY};
                font-size: 12px;
            }}
        """)
        header.setDefaultAlignment(Qt.AlignLeft)
        
        # Configurar larguras das colunas
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Produto
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Quantidade
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Preço Unit.
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Subtotal
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Ações
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # Remover
        
        self.setColumnWidth(1, 120)
        self.setColumnWidth(2, 140)
        self.setColumnWidth(3, 140)
        self.setColumnWidth(4, 140)
        self.setColumnWidth(5, 100)
        
        # Configurar aparência da tabela
        self.setAlternatingRowColors(True)
        # Make rows and header taller for better button visibility
        header.setDefaultSectionSize(52)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(64)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD_BG};
                border: none;
                border-radius: 12px;
                alternate-background-color: #F9FAFB;
                gridline-color: {BORDER_COLOR};
                font-size: 14px;
            }}
            QTableWidget::item {{
                padding: 14px 12px;
                border: none;
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QTableWidget::item:selected {{
                background-color: #EFF6FF;
                color: {PRIMARY_COLOR};
            }}
        """)
        
    def add_item(self, product_id, name, quantity, price):
        """Adiciona um item à tabela."""
        row = self.rowCount()
        self.insertRow(row)
        
        # Produto
        product_item = QTableWidgetItem(name)
        product_item.setData(Qt.UserRole, product_id)
        self.setItem(row, 0, product_item)
        
        # Quantidade
        quantity_item = QTableWidgetItem(str(quantity))
        quantity_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, 1, quantity_item)
        
        # Preço Unitário
        price_item = QTableWidgetItem(f"Kz {price:,.2f}")
        self.setItem(row, 2, price_item)
        
        # Subtotal
        subtotal = quantity * price
        subtotal_item = QTableWidgetItem(f"Kz {subtotal:,.2f}")
        subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.setItem(row, 3, subtotal_item)
        
        # Ações (editar quantidade)
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(6, 6, 6, 6)
        actions_layout.setSpacing(8)
        actions_layout.setAlignment(Qt.AlignCenter)
        actions_widget.setFixedWidth(160)
        actions_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        decrease_btn = QPushButton("-")
        decrease_btn.setFixedSize(36, 36)
        decrease_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #F3F4F6;
                color: {TEXT_PRIMARY};
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                font-weight: 700;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #E6E9F2;
            }}
        """)
        decrease_btn.setCursor(Qt.PointingHandCursor)
        
        increase_btn = QPushButton("+")
        increase_btn.setFixedSize(36, 36)
        increase_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 700;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #3B52CC;
            }}
        """)
        increase_btn.setCursor(Qt.PointingHandCursor)
        
        actions_layout.addWidget(decrease_btn)
        actions_layout.addSpacing(8)
        actions_layout.addWidget(increase_btn)
        
        self.setCellWidget(row, 4, actions_widget)
        
        # Botão remover
        remove_btn = QPushButton()
        remove_btn.setFixedSize(40, 40)
        remove_btn.setToolTip("Remover item")
        remove_btn.setIcon(QIcon.fromTheme("edit-delete"))
        remove_btn.setText("")
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFEDED;
                color: {DANGER_COLOR};
                border: 1px solid #F5C2C2;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: #FFD6D6;
            }}
        """)
        remove_btn.setCursor(Qt.PointingHandCursor)
        self.setCellWidget(row, 5, remove_btn)
        
        # Conectar sinais
        decrease_btn.clicked.connect(lambda: self._adjust_quantity(row, -1))
        increase_btn.clicked.connect(lambda: self._adjust_quantity(row, 1))
        remove_btn.clicked.connect(lambda: self._remove_item(row))
        
        return subtotal
    
    def _adjust_quantity(self, row, delta):
        """Ajusta a quantidade de um item."""
        quantity_item = self.item(row, 1)
        price_item = self.item(row, 2)
        
        if quantity_item and price_item:
            current_qty = int(quantity_item.text())
            new_qty = current_qty + delta
            
            if new_qty > 0:
                quantity_item.setText(str(new_qty))
                
                # Recalcular subtotal
                price_text = price_item.text().replace("Kz", "").replace(",", "").strip()
                price = float(price_text)
                subtotal = new_qty * price
                
                subtotal_item = self.item(row, 3)
                subtotal_item.setText(f"Kz {subtotal:,.2f}")
                
                # Emitir sinal de atualização
                self.parent().update_totals()
    
    def _remove_item(self, row):
        """Remove um item da tabela."""
        self.removeRow(row)
        self.parent().update_totals()
    
    def get_total(self):
        """Calcula o total da venda."""
        total = 0.0
        for row in range(self.rowCount()):
            subtotal_item = self.item(row, 3)
            if subtotal_item:
                subtotal_text = subtotal_item.text().replace("Kz", "").replace(",", "").strip()
                total += float(subtotal_text)
        return total
    
    def clear_table(self):
        """Limpa a tabela."""
        self.setRowCount(0)


class VendaView(QWidget):
    """Janela principal de vendas."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cart_items = []  # Lista de itens no carrinho
        self.setup_ui()
    
    def setup_ui(self):
        # Layout externo e área de conteúdo rolável
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(0)

        # Conteúdo que ficará dentro do scroll
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 20, 0, 20)
        content_layout.setSpacing(20)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # manter referências para rolagem
        self._scroll_area = scroll_area
        self._content_widget = content_widget
        
        # Configurar fundo
        self.setAutoFillBackground(True)
        from PyQt5.QtGui import QPalette
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(BG_COLOR))
        self.setPalette(palette)

        title_label = QLabel(" Nova Venda")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; margin-bottom: 10px;")
        content_layout.addWidget(title_label)
        
        # Linha 1: Informações do cliente e pesquisa
        row1_frame = RoundedFrame(radius=12)
        self.row1_frame = row1_frame
        row1_layout = QVBoxLayout(row1_frame)
        row1_layout.setContentsMargins(20, 20, 20, 20)
        row1_layout.setSpacing(15)
        
        # Cliente
        client_frame = QFrame()
        client_layout = QHBoxLayout(client_frame)
        client_layout.setContentsMargins(0, 0, 0, 0)
        client_layout.setSpacing(10)
        
        client_label = QLabel(" Cliente:")
        client_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; font-size: 14px;")
        
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Nome do cliente (opcional)")
        self.client_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY_COLOR};
            }}
        """)
        
        client_layout.addWidget(client_label)
        client_layout.addWidget(self.client_input, 1)
        
        # Pesquisa de produto
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        search_label = QLabel(" Pesquisar Produto:")
        search_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; font-size: 14px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o nome, código ou categoria do produto...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY_COLOR};
            }}
        """)
        
        self.search_btn = QPushButton("Buscar")
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #3B52CC;
            }}
        """)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_btn)

        # Autocomplete (completer) para nomes de produto
        self._completer_model = QStringListModel()
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        try:
            # prefer popup that filters contains
            from PyQt5.Qt import Qt as _QtConst
            self._completer.setFilterMode(_QtConst.MatchContains)
        except Exception:
            pass
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self.search_input.setCompleter(self._completer)
        self.search_input.textChanged.connect(self._update_completions)
        self._completer.activated.connect(self._on_completer_activated)
        
        row1_layout.addWidget(client_frame)
        row1_layout.addWidget(search_frame)
        content_layout.addWidget(row1_frame)
        
        # Linha 2: Card do produto
        self.product_card = ProductCard()
        content_layout.addWidget(self.product_card)
        
        # Linha 3: Itens da venda
        row3_frame = RoundedFrame(radius=12)
        self.row3_frame = row3_frame
        row3_layout = QVBoxLayout(row3_frame)
        row3_layout.setContentsMargins(20, 20, 20, 20)
        row3_layout.setSpacing(15)
        
        items_label = QLabel(" Itens da Venda")
        items_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            margin-bottom: 10px;
        """)
        
        self.items_table = SaleItemTable()
        row3_layout.addWidget(items_label)
        row3_layout.addWidget(self.items_table, 1)

        content_layout.addWidget(row3_frame, 1)
        
        # Linha 4: Resumo e botões
        row4_frame = RoundedFrame(radius=12)
        self.row4_frame = row4_frame
        row4_layout = QHBoxLayout(row4_frame)
        row4_layout.setContentsMargins(18, 16, 18, 16)
        row4_layout.setSpacing(12)

        # Resumo (estilizado)
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                padding: 12px 16px;
            }}
        """)
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(6)
        
        self.total_label = QLabel("Total: Kz 0,00")
        self.total_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 800;
            color: {PRIMARY_COLOR};
        """)
        
        self.items_count_label = QLabel("0 itens na venda")
        self.items_count_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 13px;")
        
        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.items_count_label)
        
        row4_layout.addWidget(summary_frame)
        row4_layout.addStretch()

        # Botões (com estilo consistente e mais visíveis)
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(12)

        self.cancel_btn = QPushButton(" Cancelar Venda")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #FFF6F6;
                color: %s;
                border: 1px solid #F5C2C2;
                border-radius: 10px;
                font-weight: 700;
                font-size: 14px;
                min-width: 140px;
            }
            QPushButton:hover { background-color: #FFECEC; }
        """ % DANGER_COLOR)

        self.sell_btn = QPushButton(" Finalizar Venda")
        self.sell_btn.setCursor(Qt.PointingHandCursor)
        self.sell_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px 22px;
                background-color: {SECONDARY_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 800;
                font-size: 14px;
                min-width: 160px;
            }}
            QPushButton:hover {{ background-color: #0DA271; }}
        """)
        self.sell_btn.setEnabled(False)

        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.sell_btn)

        row4_layout.addWidget(buttons_frame)
        content_layout.addWidget(row4_frame)

        # adicionar scroll area ao layout externo
        outer_layout.addWidget(scroll_area)
        
        # Conectar sinais
        self.setup_connections()

        # compute DB file path: walk upwards until a `database` folder is found
        file_path = Path(__file__).resolve()
        _ROOT = file_path
        for _ in range(8):
            if (_ROOT / 'database').exists():
                break
            _ROOT = _ROOT.parent
        self._db_file = _ROOT / 'database' / 'kamba_farma.db'
    
    def setup_connections(self):
        """Conecta os sinais e slots."""
        self.search_btn.clicked.connect(self.search_product)
        self.search_input.returnPressed.connect(self.search_product)
        self.product_card.add_to_cart_btn.clicked.connect(self.add_to_cart)
        self.cancel_btn.clicked.connect(self.cancel_sale)
        self.sell_btn.clicked.connect(self.finalize_sale)
    
    def search_product(self):
        """Pesquisa um produto no banco de dados."""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            QMessageBox.warning(self, "Aviso", "Digite um termo para pesquisa.")
            return
        
        # Realizar busca no banco de dados
        try:
            db_path = self._db_file
            if not db_path.exists():
                QMessageBox.critical(self, "Erro", f"Arquivo de banco de dados não encontrado: {db_path}")
                return
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            like = f"%{search_term}%"
            cur.execute(
                """
                SELECT id, nome_comercial, stock, preco_venda, codigo_barras, categoria, foto
                FROM produtos
                WHERE ativo=1 AND (nome_comercial LIKE ? OR codigo_barras LIKE ? OR categoria LIKE ?)
                ORDER BY nome_comercial LIMIT 1
                """,
                (like, like, like)
            )
            row = cur.fetchone()
            conn.close()

            if not row:
                QMessageBox.information(self, "Nenhum resultado", "Nenhum produto encontrado para o termo pesquisado.")
                return

            product_id = row['id']
            nome = row['nome_comercial']
            stock = row['stock'] or 0
            price = row['preco_venda'] or 0.0
            code = row['codigo_barras'] or ''
            category = row['categoria'] or ''
            image = row['foto']

            self.product_card.set_product_info(nome, stock, price, code, category, image)
            self.current_product_id = product_id
            self.current_product_price = float(price)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar produto: {e}")
            return

    def _update_completions(self, text: str):
        """Atualiza o modelo do completer com nomes que contenham o texto digitado."""
        term = text.strip()
        if not term:
            self._completer_model.setStringList([])
            return

        try:
            db_path = self._db_file
            if not db_path.exists():
                return
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            like = f"%{term}%"
            cur.execute("SELECT nome_comercial FROM produtos WHERE ativo=1 AND nome_comercial LIKE ? ORDER BY nome_comercial LIMIT 20", (like,))
            rows = cur.fetchall()
            conn.close()
            names = [r['nome_comercial'] for r in rows]
            self._completer_model.setStringList(names)
        except Exception:
            # don't break typing on error
            return

    def _on_completer_activated(self, text: str):
        """Quando o usuário seleciona uma sugestão, preencher o campo e buscar o produto."""
        self.search_input.setText(text)
        self.search_product()

    def set_active_nav(self, btn: QPushButton):
        """Define o botão de navegação ativo e ajusta estilos."""
        active_style = f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 700;
            }}
        """
        try:
            if btn == self.nav_sell_btn:
                btn.setStyleSheet(active_style)
        except Exception:
            pass

    def scroll_to_widget(self, widget: QWidget):
        """Rola o scroll area até que o widget fique visível no topo."""
        try:
            if not hasattr(self, '_scroll_area') or self._scroll_area is None:
                return
            # posição do widget relativa ao conteúdo
            target_y = widget.mapTo(self._content_widget, widget.rect().topLeft()).y()
            # limitar valores
            sb = self._scroll_area.verticalScrollBar()
            value = max(0, min(target_y, sb.maximum()))
            sb.setValue(value)
        except Exception:
            pass
    
    def add_to_cart(self):
        """Adiciona o produto atual ao carrinho."""
        if not hasattr(self, 'current_product_id'):
            QMessageBox.warning(self, "Aviso", "Selecione um produto primeiro.")
            return
        
        product_name = self.product_card.name_label.text()
        quantity = self.product_card.quantity_spinbox.value()
        
        # Verificar se já está no carrinho
        for i in range(self.items_table.rowCount()):
            item = self.items_table.item(i, 0)
            if item and item.data(Qt.UserRole) == self.current_product_id:
                # Atualizar quantidade
                current_qty = int(self.items_table.item(i, 1).text())
                new_qty = current_qty + quantity
                self.items_table.item(i, 1).setText(str(new_qty))
                
                # Recalcular subtotal
                subtotal = new_qty * self.current_product_price
                self.items_table.item(i, 3).setText(f"Kz {subtotal:,.2f}")
                
                self.update_totals()
                return
        
        # Adicionar novo item
        self.items_table.add_item(
            self.current_product_id,
            product_name,
            quantity,
            self.current_product_price
        )
        
        self.update_totals()
    
    def update_totals(self):
        """Atualiza os totais da venda."""
        total = self.items_table.get_total()
        item_count = self.items_table.rowCount()
        
        self.total_label.setText(f"Total: Kz {total:,.2f}")
        self.items_count_label.setText(f"{item_count} {'item' if item_count == 1 else 'itens'} na venda")
        
        # Habilitar/desabilitar botão de venda
        self.sell_btn.setEnabled(item_count > 0)
    
    def cancel_sale(self):
        """Cancela a venda atual."""
        reply = QMessageBox.question(
            self, "Cancelar Venda",
            "Tem certeza que deseja cancelar esta venda?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.clear_sale()
    
    def clear_sale(self):
        """Limpa toda a venda."""
        self.items_table.clear_table()
        self.client_input.clear()
        self.search_input.clear()
        self.product_card.set_product_info(
            "Nenhum produto selecionado",
            0,
            0.0,
            "",
            "",
            None
        )
        self.update_totals()

    def print_invoice(self, venda_id, cliente, itens, total):
        """Gera um HTML simples da fatura e abre diálogo de impressão."""
        try:
            date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Construir HTML da fatura
            html = f"""
            <html>
            <head>
            <meta charset='utf-8'>
            <style>
            body {{ font-family: Arial, Helvetica, sans-serif; color: #111; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px 6px; border-bottom: 1px solid #ddd; text-align: left; }}
            th {{ background: #f5f7fb; }}
            .right {{ text-align: right; }}
            .total {{ font-weight: 700; font-size: 1.1em; }}
            </style>
            </head>
            <body>
            <div class='header'>
                <h2>Kamba Farma</h2>
                <div>Fatura: {venda_id} — {date_str}</div>
                <div>Cliente: {cliente}</div>
            </div>
            <table>
                <thead>
                    <tr><th>Produto</th><th>Qtd</th><th class='right'>Preço Unit.</th><th class='right'>Subtotal</th></tr>
                </thead>
                <tbody>
            """

            for it in itens:
                # obter nome do produto quando possível
                produto_nome = str(it.get('produto_nome') or it.get('produto_id'))
                quantidade = int(it.get('quantidade', 0))
                preco = float(it.get('preco_unitario') or 0.0)
                subtotal = quantidade * preco
                html += f"<tr><td>{produto_nome}</td><td>{quantidade}</td><td class='right'>Kz {preco:,.2f}</td><td class='right'>Kz {subtotal:,.2f}</td></tr>"

            html += f"""
                </tbody>
            </table>
            <div style='margin-top:18px; text-align:right;'>
                <div class='total'>Total: Kz {total:,.2f}</div>
            </div>
            <div style='margin-top:12px; font-size:12px; color:#666;'>Obrigado pela preferência!</div>
            </body>
            </html>
            """

            # Preparar documento e diálogo de impressão
            doc = QTextDocument()
            doc.setHtml(html)
            printer = QPrinter()
            dialog = QPrintDialog(printer, self)
            dialog.setWindowTitle("Imprimir Fatura")
            if dialog.exec_() == QPrintDialog.Accepted:
                doc.print_(printer)
        except Exception as e:
            QMessageBox.warning(self, "Impressão", f"Falha ao imprimir fatura: {e}")
    
    def finalize_sale(self):
        """Finaliza a venda."""
        if self.items_table.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Adicione itens à venda primeiro.")
            return
        
        # TODO: Implementar lógica real de venda no banco de dados
        # Por enquanto, vamos mostrar um resumo
        
        client_name = self.client_input.text().strip()
        if not client_name:
            QMessageBox.warning(self, "Aviso", "O nome do cliente é obrigatório para registrar a venda.")
            return
        total = self.items_table.get_total()
        item_count = self.items_table.rowCount()
        
        # Persistir venda no banco
        try:
            db_path = self._db_file
            if not db_path.exists():
                QMessageBox.critical(self, "Erro", f"Arquivo de banco de dados não encontrado: {db_path}")
                return
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()

            # Inserir venda
            cur.execute("INSERT INTO vendas (usuario_id, total) VALUES (?, ?)", (None, total))
            venda_id = cur.lastrowid
            # Preparar histórico: coletar itens para gravar no historico_compra
            itens_historico = []

            # Para cada item, distribuir entre lotes disponíveis e inserir itens_venda
            for row in range(self.items_table.rowCount()):
                product_item = self.items_table.item(row, 0)
                produto_id = product_item.data(Qt.UserRole)
                quantidade = int(self.items_table.item(row, 1).text())
                price_text = self.items_table.item(row, 2).text().replace("Kz", "").replace(",", "").strip()
                preco_unit = float(price_text)
                # tentar obter o nome comercial do produto para a fatura/histórico
                try:
                    cur.execute("SELECT nome_comercial FROM produtos WHERE id = ?", (produto_id,))
                    prod_row = cur.fetchone()
                    produto_nome = prod_row['nome_comercial'] if prod_row else None
                except Exception:
                    produto_nome = None

                itens_historico.append({
                    "produto_id": produto_id,
                    "produto_nome": produto_nome,
                    "quantidade": quantidade,
                    "preco_unitario": preco_unit
                })
                quantidade_rem = quantidade

                # Distribuir por lotes FIFO (por validade mais próxima)
                while quantidade_rem > 0:
                    cur.execute(
                        "SELECT id, quantidade_atual FROM lotes WHERE produto_id = ? AND quantidade_atual > 0 AND ativo=1 ORDER BY validade ASC, id ASC LIMIT 1",
                        (produto_id,)
                    )
                    lote = cur.fetchone()
                    if lote is None:
                        # sem lotes com stock suficiente — ainda assim registrar item sem lote
                        subtotal = quantidade_rem * preco_unit
                        cur.execute(
                            "INSERT INTO itens_venda (venda_id, produto_id, lote_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                            (venda_id, produto_id, None, quantidade_rem, preco_unit, subtotal)
                        )
                        quantidade_rem = 0
                    else:
                        lote_id = lote['id']
                        lote_qtd = lote['quantidade_atual']
                        usar = min(quantidade_rem, lote_qtd)
                        subtotal = usar * preco_unit
                        cur.execute(
                            "INSERT INTO itens_venda (venda_id, produto_id, lote_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?, ?)",
                            (venda_id, produto_id, lote_id, usar, preco_unit, subtotal)
                        )
                        # Atualizar lote
                        cur.execute(
                            "UPDATE lotes SET quantidade_atual = quantidade_atual - ? WHERE id = ?",
                            (usar, lote_id)
                        )
                        quantidade_rem -= usar

                # Atualizar stock do produto
                cur.execute("UPDATE produtos SET stock = COALESCE(stock,0) - ? WHERE id = ?", (quantidade, produto_id))

            # Inserir registro no historico_compra e itens normalizados
            try:
                quantidade_total = sum(i['quantidade'] for i in itens_historico)
                produtos_json = json.dumps(itens_historico, ensure_ascii=False)
                cur.execute(
                    "INSERT INTO historico_compra (comprador_nome, produtos_comprados, quantidade_total) VALUES (?, ?, ?)",
                    (client_name, produtos_json, quantidade_total)
                )
                historico_id = cur.lastrowid
                for it in itens_historico:
                    cur.execute(
                        "INSERT INTO historico_compra_itens (historico_compra_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                        (historico_id, it['produto_id'], it['quantidade'], it.get('preco_unitario'))
                    )
            except Exception:
                # se falhar ao gravar histórico, não impedimos a venda; apenas continuar
                pass

            conn.commit()

            # Tentar imprimir fatura
            try:
                self.print_invoice(venda_id, client_name, itens_historico, total)
            except Exception:
                # não bloquear caso impressão falhe
                pass

            # Mensagem de sucesso
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Resumo da Venda")
            msg.setText(f"Venda finalizada com sucesso!\n\nCliente: {client_name}\nTotal: Kz {total:,.2f}\nItens: {item_count}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            self.clear_sale()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass


# Backwards-compatibility: expose `VendaPage` name expected elsewhere
VendaPage = VendaView

# Alias expected by SPA loader
VenderProdutoView = VendaView


if __name__ == '__main__':
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        window = VendaView()
        window.resize(1200, 900)
        window.setWindowTitle("Sistema de Vendas - Kamba Farma")
        window.show()

        sys.exit(app.exec_())