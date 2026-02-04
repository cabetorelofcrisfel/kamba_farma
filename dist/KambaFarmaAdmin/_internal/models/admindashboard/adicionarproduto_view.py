from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDoubleSpinBox, QSpinBox, QFormLayout, QScrollArea,
    QFileDialog, QMessageBox, QFrame, QComboBox, QDateEdit, QCheckBox,
    QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPainter, QPainterPath, QColor, QLinearGradient
import sqlite3
from pathlib import Path

# Paleta de cores - TEMA CLARO MODERNO
MILK_BG = "#FFFBF5"  # Fundo leitoso
CARD_BG = "#FFFFFF"  # Branco puro para cards
LIGHT_BORDER = "#E8E8E8"  # Borda cinza claro
ACCENT_BORDER = "#00BFA5"  # Borda de destaque teal
TEXT_PRIMARY = "#2C3E50"  # Azul escuro para texto principal
TEXT_SECONDARY = "#7F8C8D"  # Cinza para texto secundário
TEXT_LIGHT = "#95A5A6"  # Cinza mais claro
TEAL_PRIMARY = "#00BFA5"  # Teal principal
TEAL_LIGHT = "#E0F7FA"  # Teal muito claro para fundo
TEAL_HOVER = "#B2EBF2"  # Teal para hover
TEAL_DARK = "#00897B"
GREEN_SUCCESS = "#2ECC71"  # Verde moderno
RED_ERROR = "#E74C3C"  # Vermelho moderno
PURPLE = "#9B59B6"  # Roxo moderno
BLUE_INFO = "#3498DB"  # Azul moderno
ORANGE_ALERT = "#F39C12"  # Laranja moderno
SHADOW_COLOR = "#00000010"  # Sombra sutil


class RoundedFrame(QFrame):
    """Frame com cantos arredondados."""
    def __init__(self, radius=12, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        
        painter.fillRect(self.rect(), QColor(CARD_BG))
        painter.setPen(QColor(LIGHT_BORDER))
        painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, self.radius, self.radius)


class GradientHeader(QFrame):
    """Cabeçalho com gradiente."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gradiente de fundo
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#00BFA5"))
        gradient.setColorAt(1, QColor("#009688"))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.setClipPath(path)
        painter.fillRect(self.rect(), gradient)


class ModernInput(QLineEdit):
    """Campo de entrada moderno."""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(48)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                selection-background-color: {TEAL_PRIMARY}40;
            }}
            QLineEdit:focus {{
                border: 2px solid {TEAL_PRIMARY};
                background-color: {TEAL_LIGHT};
            }}
            QLineEdit:hover {{
                border: 1.5px solid {TEAL_PRIMARY}80;
            }}
        """)


class ModernComboBox(QComboBox):
    """ComboBox moderno."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(48)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QComboBox:hover {{
                border: 1.5px solid {TEAL_PRIMARY}80;
            }}
            QComboBox:focus {{
                border: 2px solid {TEAL_PRIMARY};
                background-color: {TEAL_LIGHT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 16px;
                height: 16px;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid {TEXT_SECONDARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: {CARD_BG};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 10px;
                selection-background-color: {TEAL_PRIMARY};
                selection-color: white;
                padding: 8px;
            }}
        """)


class ModernSpinBox(QSpinBox):
    """SpinBox moderno."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(48)
        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QSpinBox:hover {{
                border: 1.5px solid {TEAL_PRIMARY}80;
            }}
            QSpinBox:focus {{
                border: 2px solid {TEAL_PRIMARY};
                background-color: {TEAL_LIGHT};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 30px;
            }}
        """)


class ModernDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox moderno."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(48)
        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QDoubleSpinBox:hover {{
                border: 1.5px solid {TEAL_PRIMARY}80;
            }}
            QDoubleSpinBox:focus {{
                border: 2px solid {TEAL_PRIMARY};
                background-color: {TEAL_LIGHT};
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                background-color: transparent;
                border: none;
                width: 30px;
            }}
        """)


class ModernDateEdit(QDateEdit):
    """DateEdit moderno."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(48)
        self.setCalendarPopup(True)
        self.setDisplayFormat('dd/MM/yyyy')
        self.setDate(QDate.currentDate())
        self.setStyleSheet(f"""
            QDateEdit {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QDateEdit:hover {{
                border: 1.5px solid {TEAL_PRIMARY}80;
            }}
            QDateEdit:focus {{
                border: 2px solid {TEAL_PRIMARY};
                background-color: {TEAL_LIGHT};
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 40px;
            }}
        """)


class ModernCheckBox(QCheckBox):
    """CheckBox moderno."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_PRIMARY};
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                spacing: 12px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {LIGHT_BORDER};
                border-radius: 6px;
                background-color: {CARD_BG};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {TEAL_PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {TEAL_PRIMARY};
                border: 2px solid {TEAL_PRIMARY};
            }}
            QCheckBox::indicator:checked::image {{
                width: 12px;
                height: 12px;
                background-color: transparent;
            }}
        """)


class ModernButton(QPushButton):
    """Botão moderno com efeitos."""
    def __init__(self, text="", icon="", color=TEAL_PRIMARY, hover_color=TEAL_DARK, parent=None):
        super().__init__(parent)
        self.setText(f"{icon} {text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(52)
        self.color = color
        self.hover_color = hover_color
        self._update_style()
        
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px 28px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                transition: all 0.2s ease;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
                transform: translateY(-2px);
                box-shadow: 0 6px 20px {self.color}40;
            }}
            QPushButton:pressed {{
                transform: translateY(0);
                box-shadow: 0 2px 8px {self.color}40;
            }}
        """)


class AddProductPage(QWidget):
    """Página para adicionar novos produtos ao sistema"""
    
    # Emitido quando um produto é adicionado. Payload: {'id': ..., 'nome': ...}
    product_added = pyqtSignal(dict)  # Sinal emitido quando um produto é adicionado
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.foto_data = None  # Para armazenar a imagem em bytes
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface do usuário"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Configurar fundo leitoso
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(MILK_BG))
        self.setPalette(palette)

        # Cabeçalho com gradiente
        header_frame = GradientHeader()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        header_content = QHBoxLayout()
        
        # Ícone e título
        icon_label = QLabel("")
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 36px;
                color: white;
            }}
        """)
        
        title_container = QVBoxLayout()
        title_label = QLabel("Adicionar Novo Produto")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 22px;
                font-weight: 700;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
        """)
        
        subtitle_label = QLabel("Preencha os dados do produto para cadastro no sistema")
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
        """)
        
        title_container.addWidget(title_label)
        title_container.addWidget(subtitle_label)
        title_container.setSpacing(5)
        
        header_content.addWidget(icon_label)
        header_content.addSpacing(15)
        header_content.addLayout(title_container)
        header_content.addStretch()
        
        header_layout.addLayout(header_content)
        main_layout.addWidget(header_frame)

        # Área de rolagem para o formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {TEAL_PRIMARY};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {TEAL_PRIMARY}DD;
            }}
        """)
        
        form_container = QWidget()
        form_container.setStyleSheet(f"background-color: transparent;")
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(20)

        # Seção 1: Informações Básicas
        basic_info_group = QGroupBox(" Informações Básicas")
        basic_info_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {CARD_BG};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: {TEAL_LIGHT};
                color: {TEAL_PRIMARY};
                border-radius: 6px;
            }}
        """)
        
        basic_form = QGridLayout(basic_info_group)
        basic_form.setSpacing(20)
        basic_form.setContentsMargins(15, 30, 15, 15)
        
        # Campo: Nome do Produto
        self.nome_input = ModernInput("Ex: Paracetamol 500mg")
        basic_form.addWidget(QLabel("Nome do Produto*:"), 0, 0)
        basic_form.addWidget(self.nome_input, 0, 1)
        
        # Campo: Categoria
        self.categoria_combo = ModernComboBox()
        self.categoria_combo.addItems([
            "Selecione uma categoria",
            "Analgésicos",
            "Antibióticos", 
            "Anti-inflamatórios",
            "Antialérgicos",
            "Antitérmicos",
            "Antidepressivos",
            "Vitaminas",
            "Suplementos",
            "Cuidados Pessoais",
            "Primeiros Socorros",
            "Outros"
        ])
        basic_form.addWidget(QLabel("Categoria*:"), 0, 2)
        basic_form.addWidget(self.categoria_combo, 0, 3)
        
        # Campo: Princípio Ativo
        self.principio_input = ModernInput("Ex: Paracetamol (recomendado)")
        basic_form.addWidget(QLabel("Princípio Ativo:"), 1, 0)
        basic_form.addWidget(self.principio_input, 1, 1)
        
        # Campo: Forma farmacêutica
        self.forma_input = ModernInput("Ex: Comprimido")
        basic_form.addWidget(QLabel("Forma Farmacêutica*:"), 1, 2)
        basic_form.addWidget(self.forma_input, 1, 3)
        
        # Campo: Código de barras
        self.codigo_barras_input = ModernInput("Opcional / usar scanner")
        basic_form.addWidget(QLabel("Código de Barras:"), 2, 0)
        basic_form.addWidget(self.codigo_barras_input, 2, 1)
        
        # Campo: Unidade
        self.unidade_input = ModernInput("Ex: caixa, frasco, comprimido")
        basic_form.addWidget(QLabel("Unidade*:"), 2, 2)
        basic_form.addWidget(self.unidade_input, 2, 3)
        
        form_layout.addWidget(basic_info_group)

        # Seção 2: Preços e Stock
        price_stock_group = QGroupBox(" Preços e Stock")
        price_stock_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {CARD_BG};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: {TEAL_LIGHT};
                color: {TEAL_PRIMARY};
                border-radius: 6px;
            }}
        """)
        
        price_form = QGridLayout(price_stock_group)
        price_form.setSpacing(20)
        price_form.setContentsMargins(15, 30, 15, 15)
        
        # Campo: Preço de Venda
        self.preco_input = ModernDoubleSpinBox()
        self.preco_input.setRange(0.01, 999999.99)
        self.preco_input.setDecimals(2)
        self.preco_input.setPrefix("AOA ")
        self.preco_input.setValue(0.01)
        price_form.addWidget(QLabel("Preço de Venda*:"), 0, 0)
        price_form.addWidget(self.preco_input, 0, 1)
        
        # Campo: Preço de Compra
        self.preco_compra_input = ModernDoubleSpinBox()
        self.preco_compra_input.setRange(0.00, 999999.99)
        self.preco_compra_input.setDecimals(2)
        self.preco_compra_input.setPrefix("AOA ")
        self.preco_compra_input.setValue(0.00)
        price_form.addWidget(QLabel("Preço de Compra*:"), 0, 2)
        price_form.addWidget(self.preco_compra_input, 0, 3)
        
        # Campo: Stock mínimo
        self.stock_minimo_input = ModernSpinBox()
        self.stock_minimo_input.setRange(0, 999999)
        self.stock_minimo_input.setValue(0)
        price_form.addWidget(QLabel("Stock Mínimo*:"), 1, 0)
        price_form.addWidget(self.stock_minimo_input, 1, 1)
        
        # Campo: Stock atual
        self.stock_input = ModernSpinBox()
        self.stock_input.setRange(0, 999999)
        self.stock_input.setValue(0)
        price_form.addWidget(QLabel("Stock Inicial:"), 1, 2)
        price_form.addWidget(self.stock_input, 1, 3)
        
        form_layout.addWidget(price_stock_group)

        # Seção 3: Fornecedor e Lote
        supplier_group = QGroupBox(" Fornecedor e Lote")
        supplier_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {CARD_BG};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: {TEAL_LIGHT};
                color: {TEAL_PRIMARY};
                border-radius: 6px;
            }}
        """)
        
        supplier_form = QGridLayout(supplier_group)
        supplier_form.setSpacing(20)
        supplier_form.setContentsMargins(15, 30, 15, 15)
        
        # Campo: Fornecedor
        self.fornecedor_combo = ModernComboBox()
        self.fornecedor_combo.setEditable(True)
        self.fornecedor_combo.lineEdit().setPlaceholderText("Digite ou selecione um fornecedor")
        self.fornecedor_combo.addItem("Selecione...")
        self._load_fornecedores()
        supplier_form.addWidget(QLabel("Fornecedor:"), 0, 0)
        supplier_form.addWidget(self.fornecedor_combo, 0, 1)
        
        # Campo: Nome do lote
        self.nome_lote_input = ModernInput("Ex: Lote A123 (opcional)")
        supplier_form.addWidget(QLabel("Nome do Lote:"), 0, 2)
        supplier_form.addWidget(self.nome_lote_input, 0, 3)
        
        # Campo: Data de Vencimento
        self.validade_input = ModernDateEdit()
        supplier_form.addWidget(QLabel("Data de Vencimento:"), 1, 0)
        supplier_form.addWidget(self.validade_input, 1, 1)
        
        # Checkbox Sem validade
        self.sem_validade_cb = ModernCheckBox("Produto sem validade")
        self.sem_validade_cb.stateChanged.connect(lambda v: self.validade_input.setEnabled(v == 0))
        supplier_form.addWidget(self.sem_validade_cb, 1, 2, 1, 2)
        
        form_layout.addWidget(supplier_group)

        # Seção 4: Foto do Produto
        photo_group = QGroupBox(" Foto do Produto")
        photo_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {CARD_BG};
                border: 1.5px solid {LIGHT_BORDER};
                border-radius: 12px;
                padding: 20px;
                font-size: 16px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: {TEAL_LIGHT};
                color: {TEAL_PRIMARY};
                border-radius: 6px;
            }}
        """)
        
        photo_layout = QVBoxLayout(photo_group)
        photo_layout.setSpacing(20)
        photo_layout.setContentsMargins(15, 30, 15, 15)
        
        photo_content = QHBoxLayout()
        photo_content.setSpacing(30)
        
        # Preview da foto
        self.foto_preview = QLabel()
        self.foto_preview.setFixedSize(180, 180)
        self.foto_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {TEAL_LIGHT};
                border: 2px dashed {TEAL_PRIMARY}80;
                border-radius: 12px;
                color: {TEAL_PRIMARY};
                font-size: 16px;
            }}
        """)
        self.foto_preview.setAlignment(Qt.AlignCenter)
        self._update_foto_preview()
        
        # Controles da foto
        photo_controls = QVBoxLayout()
        photo_controls.setSpacing(15)
        
        btn_selecionar = ModernButton("Selecionar Imagem", "", TEAL_PRIMARY, TEAL_DARK)
        btn_selecionar.clicked.connect(self._selecionar_foto)
        
        btn_remover = ModernButton("Remover Imagem", "", RED_ERROR, "#C0392B")
        btn_remover.clicked.connect(self._remover_foto)
        
        photo_controls.addWidget(btn_selecionar)
        photo_controls.addWidget(btn_remover)
        photo_controls.addStretch()
        
        photo_content.addWidget(self.foto_preview)
        photo_content.addLayout(photo_controls)
        
        photo_layout.addLayout(photo_content)
        
        # Informações sobre a foto
        foto_info = QLabel("• Formatos suportados: JPG, PNG, BMP\n• Tamanho máximo recomendado: 2MB")
        foto_info.setStyleSheet(f"""
            font-size: 13px;
            color: {TEXT_SECONDARY};
            font-style: italic;
            padding: 12px 16px;
            background-color: {TEAL_LIGHT}40;
            border-radius: 8px;
            border-left: 4px solid {TEAL_PRIMARY};
        """)
        photo_layout.addWidget(foto_info)
        
        form_layout.addWidget(photo_group)
        
        # Adicionar espaço no final
        form_layout.addStretch()
        
        scroll_area.setWidget(form_container)
        main_layout.addWidget(scroll_area, 1)

        # Botões de ação
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet(f"background-color: transparent;")
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(20)
        
        # Botão Cancelar
        btn_cancelar = ModernButton("Cancelar", "", TEXT_SECONDARY, TEXT_PRIMARY)
        btn_cancelar.clicked.connect(self._on_cancelar)
        
        # Botão Salvar
        btn_salvar = ModernButton("Salvar Produto", "", GREEN_SUCCESS, "#27AE60")
        btn_salvar.clicked.connect(self._on_salvar)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_salvar)
        
        main_layout.addWidget(buttons_frame)

    def _update_foto_preview(self):
        """Atualiza o preview da foto"""
        if self.foto_data:
            pixmap = QPixmap()
            pixmap.loadFromData(self.foto_data)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.foto_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.foto_preview.setPixmap(scaled_pixmap)
                self.foto_preview.setStyleSheet(f"""
                    QLabel {{
                        border: 2px solid {TEAL_PRIMARY};
                        border-radius: 12px;
                        background-color: {CARD_BG};
                    }}
                """)
                return
        
        # Mostrar placeholder
        self.foto_preview.setText("\nClique para\nadicionar\nimagem")
        self.foto_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {TEAL_LIGHT};
                border: 2px dashed {TEAL_PRIMARY}80;
                border-radius: 12px;
                color: {TEAL_PRIMARY};
                font-size: 16px;
                font-weight: 500;
            }}
        """)

    def _selecionar_foto(self):
        """Abre diálogo para selecionar uma foto"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Imagem do Produto",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    self.foto_data = file.read()
                
                # Verificar tamanho (limite de 2MB)
                if len(self.foto_data) > 2 * 1024 * 1024:
                    QMessageBox.warning(
                        self,
                        "Imagem muito grande",
                        "A imagem selecionada excede 2MB. Por favor, selecione uma imagem menor."
                    )
                    self.foto_data = None
                else:
                    self._update_foto_preview()
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro ao carregar imagem",
                    f"Não foi possível carregar a imagem:\n{str(e)}"
                )
                self.foto_data = None
                self._update_foto_preview()

    def _remover_foto(self):
        """Remove a foto selecionada"""
        self.foto_data = None
        self._update_foto_preview()

    def _validar_dados(self):
        """Valida os dados do formulário"""
        nome = self.nome_input.text().strip()
        categoria = self.categoria_combo.currentText()
        preco = self.preco_input.value()
        preco_compra = self.preco_compra_input.value()
        unidade = self.unidade_input.text().strip()
        stock_minimo = self.stock_minimo_input.value()
        stock = self.stock_input.value()
        forma = self.forma_input.text().strip()
        
        # Validar nome
        if not nome:
            self._mostrar_erro("O nome do produto é obrigatório.", self.nome_input)
            return False
        
        # Validar categoria
        if categoria == "Selecione uma categoria":
            self._mostrar_erro("Por favor, selecione uma categoria.", self.categoria_combo)
            return False
        
        # Validar forma farmacêutica
        if not forma:
            self._mostrar_erro("Por favor, informe a forma farmacêutica.", self.forma_input)
            return False

        # Validar preço de venda
        if preco <= 0:
            self._mostrar_erro("O preço de venda deve ser maior que zero.", self.preco_input)
            return False
        
        # Validar preço de compra
        if preco_compra < 0:
            self._mostrar_erro("O preço de compra não pode ser negativo.", self.preco_compra_input)
            return False

        # Validar unidade
        if not unidade:
            self._mostrar_erro("Por favor, informe a unidade.", self.unidade_input)
            return False

        # Validar stock mínimo
        if stock_minimo < 0:
            self._mostrar_erro("O stock mínimo não pode ser negativo.", self.stock_minimo_input)
            return False
        
        # Validar stock
        if stock < 0:
            self._mostrar_erro("O stock não pode ser negativo.", self.stock_input)
            return False
        
        return True

    def _mostrar_erro(self, mensagem, widget):
        """Mostra uma mensagem de erro e destaca o campo"""
        QMessageBox.warning(self, "Campo inválido", mensagem)
        widget.setFocus()
        # Destacar temporariamente o campo
        estilo_original = widget.styleSheet()
        widget.setStyleSheet(estilo_original + f"border: 2px solid {RED_ERROR};")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, lambda: widget.setStyleSheet(estilo_original))

    def _load_fornecedores(self):
        try:
            # Resolve project root reliably and build path to local database copy used by this view
            db_path = Path(__file__).resolve().parents[3] / 'database' / 'kamba_farma.db'
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT id, nome FROM fornecedores WHERE ativo=1 ORDER BY nome")
            for r in cur.fetchall():
                self.fornecedor_combo.addItem(r['nome'], r['id'])
            conn.close()
        except Exception:
            pass

    def _limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        self.nome_input.clear()
        self.principio_input.clear()
        self.categoria_combo.setCurrentIndex(0)
        self.forma_input.clear()
        self.preco_input.setValue(0.01)
        self.preco_compra_input.setValue(0.00)
        self.codigo_barras_input.clear()
        self.unidade_input.clear()
        self.stock_minimo_input.setValue(0)
        self.stock_input.setValue(0)
        self.fornecedor_combo.setCurrentIndex(0)
        self.nome_lote_input.clear()
        self.validade_input.setDate(QDate.currentDate())
        self.sem_validade_cb.setChecked(False)
        self.foto_data = None
        self._update_foto_preview()

    def _on_salvar(self):
        """Salva o produto no banco de dados"""
        if not self._validar_dados():
            return
        
        try:
            # Conectar ao banco de dados
            # Resolve project root reliably and build path to local database copy used by this view
            db_path = Path(__file__).resolve().parents[3] / 'database' / 'kamba_farma.db'
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Garantir existência da tabela `produtos` compatível com o schema principal
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_comercial TEXT NOT NULL,
                    principio_ativo TEXT,
                    foto BLOB,
                    categoria TEXT,
                    preco_venda REAL DEFAULT 0.0,
                    preco_compra REAL DEFAULT 0.0,
                    stock INTEGER DEFAULT 0,
                    forma_farmaceutica TEXT,
                    codigo_barras TEXT UNIQUE,
                    unidade TEXT,
                    stock_minimo INTEGER DEFAULT 0,
                    fornecedor_padrao_id INTEGER,
                    lote_padrao_id INTEGER,
                    ativo INTEGER NOT NULL DEFAULT 1,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Definir/obter fornecedor
            fornecedor_id = None
            if self.fornecedor_combo.currentIndex() > 0:
                fornecedor_id = self.fornecedor_combo.currentData()
            else:
                typed = self.fornecedor_combo.currentText().strip()
                if typed and typed.lower() != 'selecione...':
                    try:
                        cur2 = conn.cursor()
                        cur2.execute("INSERT INTO fornecedores (nome, ativo) VALUES (?, ?)", (typed, 1))
                        fornecedor_id = cur2.lastrowid
                        conn.commit()
                        self.fornecedor_combo.addItem(typed, fornecedor_id)
                        self.fornecedor_combo.setCurrentIndex(self.fornecedor_combo.count() - 1)
                    except Exception:
                        fornecedor_id = None

            # Inserir produto principal
            cursor.execute('''
                INSERT INTO produtos (nome_comercial, principio_ativo, foto, categoria, preco_venda, preco_compra, stock, forma_farmaceutica, codigo_barras, unidade, stock_minimo, fornecedor_padrao_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.nome_input.text().strip(),
                self.principio_input.text().strip() if self.principio_input.text().strip() else None,
                self.foto_data,
                self.categoria_combo.currentText(),
                self.preco_input.value(),
                self.preco_compra_input.value(),
                int(self.stock_input.value()),
                self.forma_input.text().strip(),
                self.codigo_barras_input.text().strip() or None,
                self.unidade_input.text().strip(),
                int(self.stock_minimo_input.value()),
                fornecedor_id
            ))
            conn.commit()
            produto_id = cursor.lastrowid

            # Se foi fornecido nome do lote ou stock>0, criar lote vinculado
            nome_lote = self.nome_lote_input.text().strip()
            quantidade = int(self.stock_input.value())
            validade = None
            if not self.sem_validade_cb.isChecked():
                validade = self.validade_input.date().toString('yyyy-MM-dd')
            lote_id = None
            if nome_lote or quantidade > 0:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS lotes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        produto_id INTEGER NOT NULL,
                        numero_lote TEXT,
                        validade DATE,
                        foto BLOB,
                        quantidade_inicial INTEGER DEFAULT 0,
                        quantidade_atual INTEGER DEFAULT 0,
                        preco_compra REAL DEFAULT 0.0,
                        fornecedor_id INTEGER,
                        data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ativo INTEGER NOT NULL DEFAULT 1,
                        FOREIGN KEY(produto_id) REFERENCES produtos(id),
                        FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
                    )
                ''')
                cursor.execute(
                    "INSERT INTO lotes (produto_id, numero_lote, validade, quantidade_inicial, quantidade_atual, preco_compra, fornecedor_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (produto_id, nome_lote if nome_lote else None, validade, quantidade, quantidade, self.preco_input.value(), fornecedor_id)
                )
                conn.commit()
                lote_id = cursor.lastrowid
                cursor.execute("UPDATE produtos SET lote_padrao_id = ? WHERE id = ?", (lote_id, produto_id))
                conn.commit()

            conn.close()

            # Mostrar mensagem de sucesso
            msg = f"""
            <div style='text-align: center; padding: 20px;'>
                <div style='font-size: 48px; color: {GREEN_SUCCESS}; margin-bottom: 15px;'></div>
                <h3 style='color: {TEXT_PRIMARY}; margin-bottom: 10px;'>Produto Adicionado com Sucesso!</h3>
                <p style='color: {TEXT_SECONDARY}; line-height: 1.6;'>
                    <b>{self.nome_input.text().strip()}</b><br>
                    ID do produto: <b>{produto_id}</b>
                    {f'<br>ID do lote: <b>{lote_id}</b>' if lote_id else ''}
                </p>
            </div>
            """

            success_box = QMessageBox()
            success_box.setWindowTitle("Sucesso")
            success_box.setText(msg)
            success_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {CARD_BG};
                    border-radius: 12px;
                }}
                QMessageBox QLabel {{
                    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                }}
            """)
            success_box.exec_()

            # Limpar formulário
            self._limpar_formulario()

            # Emitir sinal com informações do produto
            try:
                self.product_added.emit({'id': produto_id, 'nome': self.nome_input.text().strip()})
            except Exception:
                try:
                    # compatibilidade: emitir sinal simples se receptor esperar sem payload
                    self.product_added.emit({})
                except Exception:
                    pass
            
        except sqlite3.Error as e:
            QMessageBox.critical(
                self,
                "Erro no banco de dados",
                f"Erro ao salvar o produto:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro inesperado",
                f"Ocorreu um erro inesperado:\n{str(e)}"
            )

    def _on_cancelar(self):
        """Cancela a adição do produto"""
        reply = QMessageBox.question(
            self,
            "Cancelar operação",
            "Tem certeza que deseja cancelar? Todos os dados não salvos serão perdidos.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._limpar_formulario()


# Teste da página (se executado diretamente)
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = AddProductPage()
    window.setWindowTitle("Adicionar Produto - Kamba Farma")
    window.resize(1200, 850)
    window.show()
    
    sys.exit(app.exec_())
    