"""View para adicionar usuário.

Exporta `AdicionarUsuarioView`, um QWidget simples com um formulário
de nome, email e senha. É instanciável sem argumentos, conforme
esperado por `usuario.py`.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
    QHBoxLayout, QPushButton, QMessageBox, QFileDialog, QComboBox,
    QFrame, QGridLayout, QGroupBox, QSpacerItem, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPalette, QColor, QPainter, QPainterPath

import sys
from pathlib import Path
# Determina o root do projeto de forma compatível com a estrutura:
# .../kamba_farma/src/models/admindashboard/adicionar_usuario.py
# portanto o root do projeto é parents[3].
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.paths import DB_DIR
from database.db import get_db_path, connect
from src.core.auth import hash_password

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
GREEN_SUCCESS = "#2ECC71"  # Verde moderno
RED_ERROR = "#E74C3C"  # Vermelho moderno
PURPLE = "#9B59B6"  # Roxo moderno
BLUE_INFO = "#3498DB"  # Azul moderno
ORANGE_ALERT = "#F39C12"  # Laranja moderno
SHADOW_COLOR = "#00000010"  # Sombra sutil


class RoundedFrame(QFrame):
    """Frame com cantos arredondados."""
    def __init__(self, radius=10, parent=None):
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


class ModernInput(QLineEdit):
    """Campo de entrada moderno."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(44)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                selection-background-color: {TEAL_LIGHT};
                selection-color: {TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {TEAL_PRIMARY};
                padding: 9px 14px;
            }}
            QLineEdit::placeholder {{
                color: {TEXT_LIGHT};
            }}
        """)


class ModernComboBox(QComboBox):
    """Combobox moderno."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(44)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QComboBox:focus {{
                border: 2px solid {TEAL_PRIMARY};
                padding: 9px 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {TEXT_LIGHT};
            }}
            QComboBox QAbstractItemView {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                selection-background-color: {TEAL_LIGHT};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 8px;
                padding: 5px;
            }}
        """)


class ModernButton(QPushButton):
    """Botão moderno com efeitos."""
    def __init__(self, text="", icon="", color=TEAL_PRIMARY, parent=None):
        super().__init__(text, parent)
        self.color = color
        self.icon_text = icon
        self.setMinimumHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                transition: all 0.2s ease;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px {color}40;
            }}
            QPushButton:pressed {{
                background-color: {color}AA;
                transform: translateY(0px);
            }}
        """)
        
        if icon:
            self.setText(f"{icon} {text}")


class PhotoFrame(QLabel):
    """Frame para foto do usuário com efeitos."""
    photo_selected = pyqtSignal(bytes)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.PointingHandCursor)
        self.photo_data = None
        self._setup_ui()
        
    def _setup_ui(self):
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {TEAL_LIGHT};
                border: 2px dashed {TEAL_PRIMARY}40;
                border-radius: 80px;
                color: {TEAL_PRIMARY};
                font-size: 13px;
                font-weight: 500;
            }}
            QLabel:hover {{
                background-color: {TEAL_HOVER};
                border: 2px dashed {TEAL_PRIMARY}80;
            }}
        """)
        self.setText("➕\nClique para\nadicionar foto")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._choose_photo()
            
    def _choose_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Escolher foto", 
            str(Path.home()), 
            "Imagens (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if path:
            try:
                with open(path, "rb") as f:
                    self.photo_data = f.read()
                
                pixmap = QPixmap()
                pixmap.loadFromData(self.photo_data)
                pixmap = pixmap.scaled(
                    140, 140, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                
                # Criar pixmap arredondado
                rounded = QPixmap(140, 140)
                rounded.fill(Qt.transparent)
                
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                
                path = QPainterPath()
                path.addEllipse(0, 0, 140, 140)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                
                self.setPixmap(rounded)
                self.setStyleSheet(f"""
                    QLabel {{
                        background-color: transparent;
                        border: 3px solid {GREEN_SUCCESS};
                        border-radius: 80px;
                    }}
                """)
                
                self.photo_selected.emit(self.photo_data)
                
            except Exception as e:
                print(f"Erro ao carregar foto: {e}")


class AdicionarUsuarioView(QWidget):
    """Formulário para adicionar um usuário."""

    # Emitted when a user is successfully saved. Payload: dict e.g. {'id':..., 'nome':...}
    user_saved = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.foto_bytes = None
        self._setup_ui()
        self._apply_modern_styles()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # Configurar fundo leitoso
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(MILK_BG))
        self.setPalette(palette)


        # Área rolável para formulário
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {MILK_BG};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {TEXT_LIGHT};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {TEAL_PRIMARY};
            }}
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet(f"background-color: {MILK_BG};")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Container principal
        container = RoundedFrame(radius=16)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(30)
        
        # Seção de foto
        photo_section = self._create_photo_section()
        container_layout.addWidget(photo_section)

        # Formulário em duas colunas
        form_section = self._create_form_section()
        container_layout.addWidget(form_section)

        # Botões de ação
        buttons_section = self._create_buttons_section()
        container_layout.addWidget(buttons_section)

        scroll_layout.addWidget(container)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, 1)

    

    def _create_photo_section(self):
        """Cria a seção de foto do usuário."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {CARD_BG};
            border-radius: 12px;
            border: 1px solid {LIGHT_BORDER};
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        title = QLabel("📷 Foto do Perfil")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
        """)
        
        # Container para foto
        photo_container = QWidget()
        photo_layout = QVBoxLayout(photo_container)
        photo_layout.setContentsMargins(0, 0, 0, 0)
        photo_layout.setAlignment(Qt.AlignCenter)
        
        self.photo_frame = PhotoFrame()
        self.photo_frame.photo_selected.connect(self._on_photo_selected)
        
        instructions = QLabel("Clique no círculo acima para adicionar uma foto")
        instructions.setStyleSheet(f"""
            font-size: 12px;
            color: {TEXT_LIGHT};
            margin-top: 10px;
        """)
        instructions.setAlignment(Qt.AlignCenter)
        
        photo_layout.addWidget(self.photo_frame)
        photo_layout.addWidget(instructions)
        
        layout.addWidget(title)
        layout.addWidget(photo_container)
        
        return frame

    def _create_form_section(self):
        """Cria a seção do formulário."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {CARD_BG};
            border-radius: 12px;
            border: 1px solid {LIGHT_BORDER};
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)
        
        # Grid de formulário
        grid = QGridLayout()
        grid.setSpacing(25)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        
        # Coluna 1 - Dados Pessoais
        col1_title = QLabel("👤 Dados Pessoais")
        col1_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {TEAL_PRIMARY};
            padding-bottom: 10px;
            border-bottom: 2px solid {TEAL_LIGHT};
        """)
        grid.addWidget(col1_title, 0, 0, 1, 1)
        
        # Nome
        nome_label = self._create_label("Nome Completo *")
        self.input_nome = ModernInput()
        self.input_nome.setPlaceholderText("Ex: João da Silva")
        grid.addWidget(nome_label, 1, 0)
        grid.addWidget(self.input_nome, 2, 0)
        
        # Número de Bilhete
        bi_label = self._create_label("Número de Bilhete *")
        self.input_numero_bi = ModernInput()
        self.input_numero_bi.setPlaceholderText("Ex: 123456789LA123")
        grid.addWidget(bi_label, 3, 0)
        grid.addWidget(self.input_numero_bi, 4, 0)
        
        # Área de Atuação
        area_label = self._create_label("Área de Atuação *")
        self.input_area_atuacao = ModernInput()
        self.input_area_atuacao.setPlaceholderText("Ex: Farmácia, Administração")
        grid.addWidget(area_label, 5, 0)
        grid.addWidget(self.input_area_atuacao, 6, 0)
        
        # Coluna 2 - Contato e Segurança
        col2_title = QLabel("🔐 Contato e Segurança")
        col2_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {TEAL_PRIMARY};
            padding-bottom: 10px;
            border-bottom: 2px solid {TEAL_LIGHT};
        """)
        grid.addWidget(col2_title, 0, 1, 1, 1)
        
        # Contato
        contacto_label = self._create_label("Contacto *")
        self.input_contacto = ModernInput()
        self.input_contacto.setPlaceholderText("Ex: +244 923 456 789")
        grid.addWidget(contacto_label, 1, 1)
        grid.addWidget(self.input_contacto, 2, 1)
        
        # Gênero
        genero_label = self._create_label("Gênero *")
        self.input_genero = ModernComboBox()
        self.input_genero.addItems(["Selecione...", "Masculino", "Feminino", "Outro", "Prefiro não informar"])
        grid.addWidget(genero_label, 3, 1)
        grid.addWidget(self.input_genero, 4, 1)
        
        # Senha
        senha_label = self._create_label("Senha *")
        self.input_senha = ModernInput()
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.setPlaceholderText("Mínimo 8 caracteres")
        grid.addWidget(senha_label, 5, 1)
        grid.addWidget(self.input_senha, 6, 1)
        
        # Confirmar Senha
        confirmar_label = self._create_label("Confirmar Senha *")
        self.input_senha_confirm = ModernInput()
        self.input_senha_confirm.setEchoMode(QLineEdit.Password)
        self.input_senha_confirm.setPlaceholderText("Digite a senha novamente")
        grid.addWidget(confirmar_label, 7, 1)
        grid.addWidget(self.input_senha_confirm, 8, 1)
        
        layout.addLayout(grid)
        
        # Nota sobre campos obrigatórios
        note = QLabel("* Campos obrigatórios")
        note.setStyleSheet(f"""
            font-size: 12px;
            color: {TEXT_LIGHT};
            font-style: italic;
            padding-top: 10px;
        """)
        layout.addWidget(note)
        
        return frame

    def _create_buttons_section(self):
        """Cria a seção de botões."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: {CARD_BG};
            border-radius: 12px;
            border: 1px solid {LIGHT_BORDER};
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Botão de limpar
        btn_limpar = ModernButton("Limpar", "🗑️", TEXT_LIGHT)
        btn_limpar.clicked.connect(self._on_cancelar)
        btn_limpar.setMinimumWidth(150)
        
        layout.addWidget(btn_limpar)
        layout.addStretch()
        
        # Botão de salvar
        btn_salvar = ModernButton("Salvar Usuário", "💾", GREEN_SUCCESS)
        btn_salvar.clicked.connect(self._on_salvar)
        btn_salvar.setMinimumWidth(200)
        
        layout.addWidget(btn_salvar)
        
        return frame

    def _create_label(self, text):
        """Cria um label estilizado."""
        label = QLabel(text)
        label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {TEXT_SECONDARY};
        """)
        return label

    def _apply_modern_styles(self):
        """Aplica estilos modernos à interface."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {MILK_BG};
                color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
        """)

    def _on_photo_selected(self, photo_data):
        """Callback quando uma foto é selecionada."""
        self.foto_bytes = photo_data

    def _on_salvar(self):
        nome = self.input_nome.text().strip()
        senha = self.input_senha.text()
        senha2 = self.input_senha_confirm.text()

        numero_bi = self.input_numero_bi.text().strip()
        area_atuacao = self.input_area_atuacao.text().strip()
        contacto = self.input_contacto.text().strip()
        genero = self.input_genero.currentText().strip()
        
        # Validação dos campos
        missing = []
        if not nome:
            missing.append('Nome')
            self._highlight_error(self.input_nome)
        else:
            self._clear_error(self.input_nome)
            
        if not numero_bi:
            missing.append('Número de Bilhete')
            self._highlight_error(self.input_numero_bi)
        else:
            self._clear_error(self.input_numero_bi)
            
        if not area_atuacao:
            missing.append('Área de Atuação')
            self._highlight_error(self.input_area_atuacao)
        else:
            self._clear_error(self.input_area_atuacao)
            
        if not contacto:
            missing.append('Contacto')
            self._highlight_error(self.input_contacto)
        else:
            self._clear_error(self.input_contacto)
            
        if not genero or genero == "Selecione...":
            missing.append('Género')
            self._highlight_error(self.input_genero)
        else:
            self._clear_error(self.input_genero)
            
        if not self.foto_bytes:
            missing.append('Foto')
            
        if not senha:
            missing.append('Senha')
            self._highlight_error(self.input_senha)
        else:
            self._clear_error(self.input_senha)
            
        if not senha2:
            missing.append('Confirmação de Senha')
            self._highlight_error(self.input_senha_confirm)
        else:
            self._clear_error(self.input_senha_confirm)

        if missing:
            self._show_notification(f"Por favor, preencha todos os campos obrigatórios:\n{', '.join(missing)}", "error")
            return

        if senha != senha2:
            self._highlight_error(self.input_senha)
            self._highlight_error(self.input_senha_confirm)
            self._show_notification("As senhas não coincidem. Por favor, digite novamente.", "error")
            return
        else:
            self._clear_error(self.input_senha)
            self._clear_error(self.input_senha_confirm)

        # Hash password
        senha_hash = hash_password(senha)

        # Save to database
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios (nome, numero_bi, area_atuacao, contacto, genero, foto, senha_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (nome, numero_bi or None, area_atuacao or None, contacto or None, genero or None, self.foto_bytes, senha_hash)
            )
            conn.commit()
            last_id = cur.lastrowid
            conn.close()
            
            # Emitir sinal para que o container (pagina) saiba que há um novo usuário
            try:
                self.user_saved.emit({'id': last_id, 'nome': nome})
            except Exception:
                pass

            # Feedback visual de sucesso
            self._show_notification(f"✅ Usuário '{nome}' cadastrado com sucesso!", "success")
            
            # Limpar formulário
            self._on_cancelar()
            
        except Exception as e:
            self._show_notification(f"❌ Erro ao salvar usuário: {str(e)}", "error")

    def _on_cancelar(self):
        """Limpa todos os campos do formulário."""
        self.input_nome.clear()
        self.input_numero_bi.clear()
        self.input_area_atuacao.clear()
        self.input_contacto.clear()
        self.input_genero.setCurrentIndex(0)
        self.input_senha.clear()
        self.input_senha_confirm.clear()
        
        # Resetar foto
        self.photo_frame.setPixmap(QPixmap())
        self.photo_frame.setText("➕\nClique para\nadicionar foto")
        self.photo_frame.setStyleSheet(f"""
            QLabel {{
                background-color: {TEAL_LIGHT};
                border: 2px dashed {TEAL_PRIMARY}40;
                border-radius: 80px;
                color: {TEAL_PRIMARY};
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        self.foto_bytes = None
        
        # Limpar erros visuais
        for widget in [self.input_nome, self.input_numero_bi, self.input_area_atuacao,
                      self.input_contacto, self.input_genero, self.input_senha,
                      self.input_senha_confirm]:
            self._clear_error(widget)

    def _highlight_error(self, widget):
        """Destaca um widget com erro."""
        if isinstance(widget, ModernInput):
            widget.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {CARD_BG};
                    color: {TEXT_PRIMARY};
                    border: 2px solid {RED_ERROR};
                    border-radius: 8px;
                    padding: 9px 14px;
                    font-size: 14px;
                    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                }}
            """)
        elif isinstance(widget, ModernComboBox):
            widget.setStyleSheet(f"""
                QComboBox {{
                    background-color: {CARD_BG};
                    color: {TEXT_PRIMARY};
                    border: 2px solid {RED_ERROR};
                    border-radius: 8px;
                    padding: 9px 14px;
                    font-size: 14px;
                    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                }}
            """)

    def _clear_error(self, widget):
        """Remove o destaque de erro de um widget."""
        if isinstance(widget, ModernInput):
            widget.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {CARD_BG};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {LIGHT_BORDER};
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-size: 14px;
                    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                }}
                QLineEdit:focus {{
                    border: 2px solid {TEAL_PRIMARY};
                    padding: 9px 14px;
                }}
            """)
        elif isinstance(widget, ModernComboBox):
            widget.setStyleSheet(f"""
                QComboBox {{
                    background-color: {CARD_BG};
                    color: {TEXT_PRIMARY};
                    border: 1px solid {LIGHT_BORDER};
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-size: 14px;
                    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                }}
                QComboBox:focus {{
                    border: 2px solid {TEAL_PRIMARY};
                    padding: 9px 14px;
                }}
            """)

    def _show_notification(self, message, type="info"):
        """Exibe uma notificação moderna."""
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtCore import QTimer, QPropertyAnimation
        
        notification = QLabel(message, self)
        
        colors = {
            "success": GREEN_SUCCESS,
            "error": RED_ERROR,
            "warning": ORANGE_ALERT,
            "info": TEAL_PRIMARY
        }
        
        color = colors.get(type, TEAL_PRIMARY)
        
        notification.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 14px 24px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                box-shadow: 0 6px 20px {color}40;
                margin: 10px;
            }}
        """)
        
        notification.adjustSize()
        notification.move(self.width() - notification.width() - 30, 30)
        notification.show()
        notification.raise_()
        
        # Animação de entrada
        notification.setWindowOpacity(0)
        anim = QPropertyAnimation(notification, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        
        # Timer para remover
        QTimer.singleShot(4000, lambda: self._fade_out_notification(notification))
    
    def _fade_out_notification(self, notification):
        """Remove a notificação com animação."""
        anim = QPropertyAnimation(notification, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.finished.connect(notification.deleteLater)
        anim.start()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Estilo global moderno
    app.setStyleSheet(f"""
        QApplication {{
            background-color: {MILK_BG};
        }}
    """)
    
    window = AdicionarUsuarioView()
    window.setWindowTitle("Cadastrar Usuário - Kamba Farma")
    window.resize(1200, 900)
    window.show()
    
    sys.exit(app.exec_())