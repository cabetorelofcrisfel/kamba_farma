from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QWidget as QWidgetLocal,
    QGridLayout, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette

import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` and other top-level packages are importable
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.paths import DB_DIR
from database.db import get_db_path, connect


class CatalogoView(QWidget):
    """Lista os produtos com foto, preço e nome do banco de dados."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_products()

    def _setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Configurar cor de fundo
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f7fa"))
        self.setPalette(palette)

        # Título com estilo aprimorado
        title_container = QFrame()
        title_container.setFrameShape(QFrame.NoFrame)
        title_layout = QVBoxLayout(title_container)
        
        title = QLabel(" Catálogo de Produtos")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 12px;
                background-color: white;
                border-radius: 10px;
                border: 2px solid #e0e0e0;
            }
        """)
        title.setFixedHeight(60)
        
        subtitle = QLabel("Navegue pelos nossos produtos disponíveis")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #7f8c8d; padding: 5px;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        main_layout.addWidget(title_container)

        # Área de rolagem com estilo
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #e0e0e0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #95a5a6;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7f8c8d;
            }
        """)

        # Container dos produtos - ALTERADO: Remove alinhamento central
        self.container = QWidgetLocal()
        self.container.setStyleSheet("background-color: transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setHorizontalSpacing(20)
        self.grid.setVerticalSpacing(25)
        # REMOVIDO: self.grid.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        # Adicionado: Alinha conteúdo ao topo e à esquerda
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Configurar as colunas para não se expandirem igualmente
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 0)
        self.grid.setColumnStretch(2, 0)
        self.grid.setColumnStretch(3, 0)
        
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

    def _create_product_card(self, name, price, photo_bytes):
        # Card principal
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setLineWidth(1)
        card.setFixedSize(200, 280)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #e0e0e0;
            }
            QFrame:hover {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        # Container da imagem
        img_container = QFrame()
        img_container.setFixedSize(150, 150)
        img_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(5, 5, 5, 5)
        
        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        img.setFixedSize(140, 140)
        
        if photo_bytes:
            pix = QPixmap()
            if pix.loadFromData(photo_bytes):
                # Calcular o tamanho mantendo proporção
                pix = pix.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img.setPixmap(pix)
                # Centralizar a imagem
                img.setAlignment(Qt.AlignCenter)
            else:
                img.setText("")
                img.setStyleSheet("font-size: 48px; color: #bdc3c7;")
        else:
            img.setText("")
            img.setStyleSheet("font-size: 48px; color: #bdc3c7;")
        
        img_layout.addWidget(img)
        
        # Nome do produto
        name_label = QLabel(name)
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setMaximumHeight(40)
        name_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                font-size: 14px;
                color: #2c3e50;
                padding: 5px;
            }
        """)
        
        # Preço
        price_label = QLabel(f"AOA {price:,.2f}")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: 700;
                font-size: 16px;
                padding: 8px 12px;
                background-color: #f1f8e9;
                border-radius: 8px;
                border: 1px solid #c8e6c9;
            }
        """)
        
        # Adicionar widgets ao layout
        layout.addWidget(img_container, 0, Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        
        # Espaçador no final para manter o alinhamento
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        return card

    def _load_products(self):
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, nome_comercial, foto, preco_venda FROM produtos WHERE ativo=1 ORDER BY nome_comercial")
            rows = cur.fetchall()
            conn.close()

            if not rows:
                # Mensagem quando não há produtos
                no_products = QLabel("Nenhum produto disponível no momento")
                no_products.setAlignment(Qt.AlignCenter)
                no_products_font = QFont()
                no_products_font.setPointSize(16)
                no_products.setFont(no_products_font)
                no_products.setStyleSheet("color: #95a5a6; padding: 50px;")
                self.grid.addWidget(no_products, 0, 0)
                return

            # Número fixo de colunas
            cols = 4
            
            row = 0
            col = 0
            for r in rows:
                name = r['nome_comercial'] if 'nome_comercial' in r.keys() else r[1]
                price = r['preco_venda'] if 'preco_venda' in r.keys() else (r[3] if len(r) > 3 else 0)
                photo = r['foto'] if 'foto' in r.keys() else (r[2] if len(r) > 2 else None)
                card = self._create_product_card(name, price or 0.0, photo)
                # ALTERADO: Adiciona sem alinhamento central, apenas na posição grid[row][col]
                self.grid.addWidget(card, row, col)
                col += 1
                if col >= cols:
                    col = 0
                    row += 1

            # Adicionar um widget vazio que se expande para empurrar tudo para a esquerda
            # Isso evita que os cards fiquem centralizados quando há poucos produtos
            if col > 0:  # Se a última linha não está completa
                for c in range(col, cols):
                    spacer = QWidget()
                    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    self.grid.addWidget(spacer, row, c)
            
            # Adicionar uma coluna de expansão à direita para manter os cards à esquerda
            self.grid.setColumnStretch(cols, 1)

        except Exception as e:
            # Mensagem de erro melhorada
            error_container = QFrame()
            error_container.setStyleSheet("""
                QFrame {
                    background-color: #ffebee;
                    border-radius: 10px;
                    border: 1px solid #ffcdd2;
                    padding: 20px;
                }
            """)
            error_layout = QVBoxLayout(error_container)
            
            error_icon = QLabel("")
            error_icon.setAlignment(Qt.AlignCenter)
            error_icon.setStyleSheet("font-size: 32px; margin-bottom: 10px;")
            
            error_label = QLabel(f"Erro ao carregar produtos:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: #c62828; font-weight: 500;")
            
            error_layout.addWidget(error_icon)
            error_layout.addWidget(error_label)
            
            self.grid.addWidget(error_container, 0, 0, 1, 3)