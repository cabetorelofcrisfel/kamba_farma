from pathlib import Path
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFormLayout, QLineEdit,
    QDateEdit, QSpinBox, QDoubleSpinBox, QComboBox, QFileDialog, QMessageBox,
    QHBoxLayout, QFrame, QSizePolicy, QScrollArea, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QPainterPath

# Ensure project root is on sys.path so `src` and other top-level packages are importable
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.paths import DB_DIR
from database.db import connect, get_db_path

from colors import *
# Local aliases and helpers
CARD_BG = WHITE
MILK_BG = BACKGROUND_GRAY
TEAL_PRIMARY = PRIMARY_COLOR
TEAL_LIGHT = "#E6F9FB"  # light variant of PRIMARY_COLOR
TEAL_HOVER = "#CFF8FA"
LIGHT_BORDER = "#E8E8E8"
BORDER_COLOR = BORDER_COLOR
TEXT_PRIMARY = TEXT_PRIMARY
TEXT_SECONDARY = "#6B7280"
TEXT_LIGHT = "#9CA3AF"

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


class AdicionarLoteView(QWidget):
    """Formulário para adicionar um lote e atualizar stock do produto."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.foto_data = None  # Para armazenar a imagem em bytes
        self.setup_ui()
        self.load_choices()
        
        # Configurar fundo
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(BG_COLOR))
        self.setPalette(palette)

    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Área de rolagem para formulários longos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #F3F4F6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #D1D5DB;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9CA3AF;
            }
        """)
        
        # Widget principal do scroll
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(25)
        
        # Cabeçalho
        header_frame = RoundedFrame(radius=12)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(12)
        
        title = QLabel(" Adicionar Novo Lote")
        title_font = QFont("Segoe UI", 20, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        
        subtitle = QLabel("Preencha os dados do novo lote de produtos")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        container_layout.addWidget(header_frame)
        
        # Formulário principal
        form_frame = RoundedFrame(radius=12)
        form_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(25)
        
        # Seção de informações básicas
        basic_group = QGroupBox(" Informações Básicas")
        basic_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 15px;
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 20px;
                background-color: {CARD_BG};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }}
        """)
        
        basic_form = QFormLayout()
        basic_form.setContentsMargins(15, 25, 15, 15)
        basic_form.setHorizontalSpacing(20)
        basic_form.setVerticalSpacing(15)
        basic_form.setLabelAlignment(Qt.AlignLeft)
        
        # Produto
        produto_label = QLabel("Produto*:")
        produto_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; min-width: 150px;")
        
        self.produto_cb = QComboBox()
        self.produto_cb.setMinimumHeight(44)
        self.produto_cb.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 300px;
            }}
            QComboBox:hover {{
                border-color: {PRIMARY_COLOR}80;
            }}
            QComboBox:focus {{
                border-color: {PRIMARY_COLOR};
                background-color: #F8FAFF;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
        """)
        
        # Número do Lote
        lote_label = QLabel("Número do Lote:")
        lote_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; min-width: 150px;")
        
        self.numero_lote = QLineEdit()
        self.numero_lote.setPlaceholderText("Ex: LOTE2024-001")
        self.numero_lote.setMinimumHeight(44)
        self.numero_lote.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY_COLOR};
                background-color: #F8FAFF;
            }}
            QLineEdit::placeholder {{
                color: {TEXT_LIGHT};
            }}
        """)
        
        # Validade
        validade_label = QLabel("Data de Validade*:")
        validade_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; min-width: 150px;")
        
        self.validade = QDateEdit()
        self.validade.setCalendarPopup(True)
        self.validade.setDate(QDate.currentDate().addYears(1))
        self.validade.setMinimumHeight(44)
        self.validade.setStyleSheet(f"""
            QDateEdit {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
            }}
            QDateEdit:focus {{
                border-color: {PRIMARY_COLOR};
                background-color: #F8FAFF;
            }}
            QDateEdit::drop-down {{
                border: none;
                width: 40px;
            }}
        """)
        
        # Quantidade
        quantidade_label = QLabel("Quantidade*:")
        quantidade_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; min-width: 150px;")
        
        self.quantidade = QSpinBox()
        self.quantidade.setRange(1, 10_000_000)
        self.quantidade.setValue(1)
        self.quantidade.setMinimumHeight(44)
        self.quantidade.setStyleSheet(f"""
            QSpinBox {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
            }}
            QSpinBox:focus {{
                border-color: {PRIMARY_COLOR};
                background-color: #F8FAFF;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 25px;
                border: none;
            }}
        """)
        
        basic_form.addRow(produto_label, self.produto_cb)
        basic_form.addRow(lote_label, self.numero_lote)
        basic_form.addRow(validade_label, self.validade)
        basic_form.addRow(quantidade_label, self.quantidade)
        
        basic_group.setLayout(basic_form)
        form_layout.addWidget(basic_group)
        
        # Seção de valores e fornecedor
        values_group = QGroupBox(" Valores e Fornecedor")
        values_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 15px;
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 20px;
                background-color: {CARD_BG};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }}
        """)
        
        values_form = QFormLayout()
        values_form.setContentsMargins(15, 25, 15, 15)
        values_form.setHorizontalSpacing(20)
        values_form.setVerticalSpacing(15)
        
        # Preço de Compra
        preco_label = QLabel("Preço de Compra*:")
        preco_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; min-width: 150px;")
        
        self.preco_compra = QDoubleSpinBox()
        self.preco_compra.setRange(0, 1e9)
        self.preco_compra.setDecimals(2)
        self.preco_compra.setPrefix("Kz ")
        self.preco_compra.setValue(0.0)
        self.preco_compra.setMinimumHeight(44)
        self.preco_compra.setStyleSheet(f"""
            QDoubleSpinBox {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
            }}
            QDoubleSpinBox:focus {{
                border-color: {PRIMARY_COLOR};
                background-color: #F8FAFF;
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                width: 25px;
                border: none;
            }}
        """)
        
        # Fornecedor
        fornecedor_label = QLabel("Fornecedor:")
        fornecedor_label.setStyleSheet(f"font-weight: 600; color: {TEXT_PRIMARY}; min-width: 150px;")
        
        self.fornecedor_cb = QComboBox()
        self.fornecedor_cb.setMinimumHeight(44)
        self.fornecedor_cb.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 15px;
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 300px;
            }}
            QComboBox:hover {{
                border-color: {PRIMARY_COLOR}80;
            }}
            QComboBox:focus {{
                border-color: {PRIMARY_COLOR};
                background-color: #F8FAFF;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 40px;
            }}
        """)
        
        values_form.addRow(preco_label, self.preco_compra)
        values_form.addRow(fornecedor_label, self.fornecedor_cb)
        
        values_group.setLayout(values_form)
        form_layout.addWidget(values_group)
        
        # Seção de foto
        foto_group = QGroupBox(" Foto do Lote (Opcional)")
        foto_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 15px;
                color: {TEXT_PRIMARY};
                border: 1.5px solid {BORDER_COLOR};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 20px;
                background-color: {CARD_BG};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }}
        """)
        
        foto_layout = QVBoxLayout()
        foto_layout.setContentsMargins(15, 25, 15, 15)
        foto_layout.setSpacing(15)
        
        # Preview da foto
        self.foto_preview = QLabel()
        self.foto_preview.setFixedSize(150, 150)
        self.foto_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
        """)
        self.foto_preview.setAlignment(Qt.AlignCenter)
        self._update_foto_preview()
        
        # Botões de foto
        foto_btn_layout = QHBoxLayout()
        
        # Botão para escolher foto
        self.foto_btn = QPushButton(" Escolher Imagem")
        self.foto_btn.setMinimumHeight(44)
        self.foto_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background-color: #3B52CC;
            }}
        """)
        self.foto_btn.setCursor(Qt.PointingHandCursor)
        self.foto_btn.clicked.connect(self.choose_foto)
        
        # Botão para remover foto
        self.remover_foto_btn = QPushButton(" Remover Imagem")
        self.remover_foto_btn.setMinimumHeight(44)
        self.remover_foto_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER_COLOR}20;
                color: {DANGER_COLOR};
                border: 1px solid {DANGER_COLOR}40;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background-color: {DANGER_COLOR}30;
            }}
        """)
        self.remover_foto_btn.setCursor(Qt.PointingHandCursor)
        self.remover_foto_btn.clicked.connect(self.remover_foto)
        
        foto_btn_layout.addWidget(self.foto_btn)
        foto_btn_layout.addWidget(self.remover_foto_btn)
        foto_btn_layout.addStretch()
        
        # Layout para preview e botões
        foto_content_layout = QHBoxLayout()
        foto_content_layout.addWidget(self.foto_preview)
        foto_content_layout.addLayout(foto_btn_layout)
        foto_content_layout.addStretch()
        
        foto_layout.addLayout(foto_content_layout)
        
        # Informações sobre a foto
        foto_info = QLabel("• Formatos suportados: JPG, PNG, BMP\n• Tamanho máximo recomendado: 2MB")
        foto_info.setStyleSheet(f"""
            font-size: 12px;
            color: {TEXT_SECONDARY};
            font-style: italic;
            padding: 10px;
            background-color: {BG_COLOR};
            border-radius: 6px;
        """)
        foto_layout.addWidget(foto_info)
        
        foto_group.setLayout(foto_layout)
        form_layout.addWidget(foto_group)
        
        container_layout.addWidget(form_frame)
        
        # Botões de ação
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("background: transparent;")
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        buttons_layout.setSpacing(15)
        buttons_layout.addStretch()
        
        # Botão Cancelar
        self.cancel_btn = QPushButton(" Cancelar")
        self.cancel_btn.setMinimumHeight(50)
        self.cancel_btn.setMinimumWidth(150)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #F3F4F6;
                color: {TEXT_SECONDARY};
                border: 1.5px solid #E5E7EB;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: #E5E7EB;
                color: {TEXT_PRIMARY};
            }}
        """)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.on_cancel)
        
        # Botão Salvar
        self.save_btn = QPushButton(" Salvar Lote")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SECONDARY_COLOR};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: #0DA271;
            }}
        """)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.on_save)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        container_layout.addWidget(buttons_frame)
        container_layout.addStretch()
        
        scroll_area.setWidget(container_widget)
        main_layout.addWidget(scroll_area)

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
                self.foto_preview.setStyleSheet("")
                return
        
        # Mostrar placeholder
        self.foto_preview.setText("\nSem\nimagem")
        self.foto_preview.setStyleSheet(f"""
            QLabel {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                font-size: 36px;
                color: {TEXT_SECONDARY};
            }}
        """)

    def load_choices(self):
        """Carrega produtos e fornecedores dos comboboxes."""
        db_path = get_db_path(DB_DIR)
        conn = connect(db_path)
        cur = conn.cursor()
        
        try:
            # Produtos
            cur.execute("SELECT id, nome_comercial FROM produtos WHERE ativo=1 ORDER BY nome_comercial")
            produtos = cur.fetchall()
            
            self.produto_cb.clear()
            for p in produtos:
                self.produto_cb.addItem(f"{p['nome_comercial']}", p['id'])
            
            if produtos:
                self.produto_cb.setCurrentIndex(0)
            
            # Fornecedores
            cur.execute("SELECT id, nome FROM fornecedores WHERE ativo=1 ORDER BY nome")
            fornecedores = cur.fetchall()
            
            self.fornecedor_cb.clear()
            self.fornecedor_cb.addItem("— Selecione um fornecedor —", None)
            
            for f in fornecedores:
                self.fornecedor_cb.addItem(f"{f['nome']}", f['id'])
                
        except Exception as e:
            print(f"Erro ao carregar opções: {e}")
        finally:
            conn.close()

    def choose_foto(self):
        """Abre diálogo para escolher imagem."""
        fn, _ = QFileDialog.getOpenFileName(
            self, 
            "Escolher imagem do lote", 
            "", 
            "Imagens (*.png *.jpg *.jpeg *.bmp);;Todos os arquivos (*.*)"
        )
        if fn:
            try:
                with open(fn, 'rb') as f:
                    self.foto_data = f.read()
                
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
                QMessageBox.warning(self, "Erro", f"Não foi possível ler a imagem selecionada: {str(e)}")

    def remover_foto(self):
        """Remove a foto selecionada"""
        self.foto_data = None
        self._update_foto_preview()

    def on_cancel(self):
        """Limpa o formulário."""
        self.numero_lote.clear()
        self.validade.setDate(QDate.currentDate().addYears(1))
        self.quantidade.setValue(1)
        self.preco_compra.setValue(0.0)
        self.foto_data = None
        self._update_foto_preview()
        self.fornecedor_cb.setCurrentIndex(0)
        
        if self.produto_cb.count() > 0:
            self.produto_cb.setCurrentIndex(0)

    def on_save(self):
        """Salva o lote no banco de dados."""
        # Validações
        if self.produto_cb.count() == 0:
            QMessageBox.warning(self, "Aviso", "Nenhum produto disponível para associar ao lote.")
            return
        
        produto_id = self.produto_cb.currentData()
        
        if not produto_id:
            QMessageBox.warning(self, "Aviso", "Selecione um produto válido.")
            return
        
        if self.quantidade.value() <= 0:
            QMessageBox.warning(self, "Aviso", "A quantidade deve ser maior que zero.")
            return
        
        if self.preco_compra.value() <= 0:
            QMessageBox.warning(self, "Aviso", "O preço de compra deve ser maior que zero.")
            return
        
        # Coletar dados
        numero_lote = self.numero_lote.text().strip() or None
        validade = self.validade.date().toString('yyyy-MM-dd')
        quantidade = int(self.quantidade.value())
        preco = float(self.preco_compra.value())
        fornecedor_id = self.fornecedor_cb.currentData()
        foto_bytes = self.foto_data  # Já temos os bytes da imagem
        
        # Salvar no banco
        db_path = get_db_path(DB_DIR)
        conn = connect(db_path)
        
        try:
            cur = conn.cursor()
            
            # Inserir lote
            cur.execute(
                """
                INSERT INTO lotes (
                    produto_id, numero_lote, validade, foto, 
                    quantidade_inicial, quantidade_atual, preco_compra, fornecedor_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    produto_id, numero_lote, validade, 
                    sqlite3.Binary(foto_bytes) if foto_bytes else None,
                    quantidade, quantidade, preco, fornecedor_id
                )
            )
            
            # Atualizar stock do produto
            cur.execute(
                "UPDATE produtos SET stock = COALESCE(stock, 0) + ? WHERE id = ?",
                (quantidade, produto_id)
            )
            
            conn.commit()
            
            # Mensagem de sucesso
            QMessageBox.information(
                self, 
                "✅ Sucesso", 
                "Lote adicionado com sucesso!\n\n"
                f"Produto: {self.produto_cb.currentText()}\n"
                f"Quantidade: {quantidade}\n"
                f"Validade: {validade}"
            )
            
            # Limpar formulário
            self.on_cancel()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(
                self, 
                "❌ Erro", 
                f"Erro ao salvar lote:\n{str(e)}"
            )
        finally:
            conn.close()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = AdicionarLoteView()
    window.resize(900, 800)
    window.setWindowTitle("Adicionar Lote - Kamba Farma")
    window.show()
    
    sys.exit(app.exec_())