"""SPA entry for usuario views.

Provides `UsuarioPage` which dynamically loads views from the
`usuario/` subfolder. Each view file should expose one QWidget
class used below. If a view is missing, a placeholder label is shown.
"""

from pathlib import Path
import importlib.util
import sys
from typing import Optional

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, 
    QLabel, QApplication, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt5.QtGui import QFont

# Paleta de cores - TEMA CLARO COM FUNDO LEITE
MILK_BG = "#FFFBF5"  # Cor de leite/off-white quente
LIGHT_CARD = "#FFFFFF"
LIGHT_BORDER = "#E8DECD"  # Borda mais suave
LIGHT_HOVER = "#F5F0E8"  # Hover sutil
DARK_TEXT = "#2C2C2C"  # Texto escuro suave
GRAY_TEXT = "#6C757D"
TEAL_PRIMARY = "#00BFA5"
TEAL_DARK = "#00897B"
GREEN_SUCCESS = "#28A745"
RED_ERROR = "#DC3545"
PURPLE = "#6F42C1"
BLUE_INFO = "#007BFF"
ORANGE_ALERT = "#FD7E14"


def _load_view_from_path(path: Path, class_name: str) -> Optional[QWidget]:
    """Import `class_name` from `path` and return an instance, or None."""
    try:
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        mod_name = f"_usuario_dynamic_{path.stem}"
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        cls = getattr(module, class_name, None)
        if cls is None:
            return None
        return cls()
    except Exception:
        return None


class UsuarioPage(QWidget):
    """SPA container for usuario-related views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.views_dir = Path(__file__).parent / "."
        self._setup_ui()

        # Apply milk theme
        self.setStyleSheet(f"""
            QWidget {{ 
                background-color: {MILK_BG}; 
                color: {DARK_TEXT};
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QStackedWidget {{
                background-color: {MILK_BG};
                border: none;
            }}
        """)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barra superior de menu horizontal
        menu_widget = QWidget()
        menu_widget.setFixedHeight(80)
        menu_widget.setStyleSheet(f"""
            background-color: {LIGHT_CARD};
            border-bottom: 1px solid {LIGHT_BORDER};
            border-radius: 0px 0px 12px 12px;
            margin: 0px 15px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.04);
        """)
        
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setContentsMargins(20, 0, 20, 0)
        menu_layout.setSpacing(5)

        # Título do menu (lado esquerdo)
        menu_title = QLabel(" GESTÃO DE USUÁRIOS")
        menu_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        menu_title.setStyleSheet(f"""
            color: {DARK_TEXT};
            padding: 0px 15px 0px 0px;
            border-right: 1px solid {LIGHT_BORDER};
        """)
        menu_layout.addWidget(menu_title)

        # Botões do menu (centro)
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_lista = QPushButton("Lista")
        self.btn_registrados = QPushButton(" Registrados")
        self.btn_permissoes = QPushButton(" Permissões")
        self.btn_logs = QPushButton(" Logs")
        self.btn_config = QPushButton(" Configurações")

        # Configurar botões
        buttons = [
            self.btn_adicionar, self.btn_lista, self.btn_registrados,
            self.btn_permissoes, self.btn_logs, self.btn_config
        ]
        
        for btn in buttons:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setMinimumWidth(120)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {GRAY_TEXT};
                    border: none;
                    text-align: center;
                    padding: 0px 15px;
                    font-size: 13px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                    border-radius: 8px;
                    margin: 0px 3px;
                    transition: all 0.2s ease;
                }}
                QPushButton:checked {{
                    background-color: {TEAL_PRIMARY}15;
                    color: {TEAL_PRIMARY};
                    border: 1.5px solid {TEAL_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {LIGHT_HOVER};
                    color: {DARK_TEXT};
                    transform: translateY(-1px);
                }}
                QPushButton:checked:hover {{
                    background-color: {TEAL_PRIMARY}20;
                    color: {TEAL_PRIMARY};
                }}
            """)

        # Adicionar botões ao layout
        for btn in buttons:
            menu_layout.addWidget(btn)
        
        # Espaçador para empurrar o status para direita
        menu_layout.addStretch()

        # Status (lado direito)
        status_widget = QFrame()
        status_widget.setStyleSheet(f"""
            background-color: {LIGHT_HOVER};
            border-radius: 8px;
            padding: 8px 15px;
            border: 1px solid {LIGHT_BORDER};
        """)
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(5, 5, 5, 5)
        status_layout.setSpacing(10)
        
        # Ícone de status
        status_icon = QLabel("")
        status_icon.setStyleSheet("font-size: 14px;")
        
        status_label = QLabel("Sistema Ativo")
        status_label.setStyleSheet(f"""
            font-size: 12px;
            color: {GRAY_TEXT};
            font-weight: 600;
        """)
        
        status_layout.addWidget(status_icon)
        status_layout.addWidget(status_label)
        menu_layout.addWidget(status_widget)

        # Área de conteúdo - StackedWidget
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {MILK_BG};")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {MILK_BG};
                border: none;
                border-radius: 12px;
            }}
        """)
        # Mapa de views carregadas dinamicamente (class_name -> widget instance)
        self.loaded_views = {}
        self._load_views()
        
        content_layout.addWidget(self.stack)

        # Conectar sinais
        self.btn_adicionar.clicked.connect(lambda: self._select(0))
        self.btn_lista.clicked.connect(lambda: self._select(1))
        self.btn_registrados.clicked.connect(lambda: self._select(2))
        self.btn_permissoes.clicked.connect(lambda: self._select(3))
        self.btn_logs.clicked.connect(lambda: self._select(4))
        self.btn_config.clicked.connect(lambda: self._select(5))

        # Selecionar primeiro item
        self.btn_adicionar.setChecked(True)
        # Mostrar a view inicial (Adicionar) imediatamente
        self._select(0)

        # Adicionar widgets ao layout principal
        main_layout.addWidget(menu_widget)
        main_layout.addWidget(content_widget, 1)

    def _select(self, index: int):
        """Seleciona a view pelo índice"""
        buttons = [
            self.btn_adicionar, self.btn_lista, self.btn_registrados,
            self.btn_permissoes, self.btn_logs, self.btn_config
        ]
        
        for i, btn in enumerate(buttons):
            btn.setChecked(i == index)
        
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            
            # Adicionar animação de transição
            self.stack.setProperty("opacity", 0.0)
            anim = QPropertyAnimation(self.stack, b"windowOpacity")
            anim.setDuration(250)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()

    def _load_views(self):
        """Carrega dinamicamente todas as views"""
        views = [
            (self.views_dir / "adicionar_usuario.py", "AdicionarUsuarioView"),
            (self.views_dir / "usuarios_view.py", "UsuariosView"),
            (self.views_dir / "usuarios_registrados.py", "UsuariosRegistradosView"),
            (self.views_dir / "permissoes_view.py", "PermissoesView"),
            (self.views_dir / "logs_view.py", "LogsView"),
            (self.views_dir / "config_view.py", "ConfigView"),
        ]

        for path, class_name in views:
            widget = _load_view_from_path(path, class_name)
            if widget is None:
                # Criar placeholder se a view não existir
                placeholder = QWidget()
                placeholder.setStyleSheet(f"""
                    background-color: {LIGHT_CARD};
                    border-radius: 12px;
                    border: 2px dashed {LIGHT_BORDER};
                """)
                
                placeholder_layout = QVBoxLayout(placeholder)
                placeholder_layout.setContentsMargins(40, 40, 40, 40)
                placeholder_layout.setAlignment(Qt.AlignCenter)
                
                placeholder_label = QLabel(
                    f"<div style='text-align: center;'>"
                    f"<h3 style='color:{TEAL_PRIMARY}; margin-bottom: 15px; font-size: 20px;'> VIEW DE USUÁRIOS</h3>"
                    f"<p style='color:{GRAY_TEXT}; font-size: 14px; line-height: 1.6; max-width: 500px;'>"
                    f"<b>Classe:</b> {class_name}<br>"
                    f"<b>Arquivo:</b> {path.name}<br><br>"
                    f"Crie este arquivo na pasta <code>usuario/</code><br>"
                    f"com uma classe chamada <code>{class_name}</code><br>"
                    f"que herde de <code>QWidget</code>."
                    f"</p>"
                    f"</div>"
                )
                
                placeholder_label.setWordWrap(True)
                placeholder_layout.addWidget(placeholder_label)
                self.stack.addWidget(placeholder)
            else:
                # Configurar estilo da view carregada
                widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {MILK_BG};
                        color: {DARK_TEXT};
                        border-radius: 12px;
                    }}
                """)
                
                # Envolver em um container para margens
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(widget)
                
                self.stack.addWidget(container)

                # Guardar referência da view real para comunicações posteriores
                try:
                    self.loaded_views[class_name] = widget
                except Exception:
                    pass

                # Conectar sinal de usuário salvo (se a view o expuser)
                if hasattr(widget, 'user_saved'):
                    try:
                        widget.user_saved.connect(self._on_user_saved)
                    except Exception:
                        pass

                # Se a view tiver um método setup_style, chamá-lo
                if hasattr(widget, 'setup_style'):
                    widget.setup_style()

    def _on_user_saved(self, user_info):
        """Handler chamado quando `AdicionarUsuarioView` emite `user_saved`.

        Atualiza a lista (se possível) e troca para a aba de lista.
        """
        nome = user_info.get('nome', '')
        try:
            self.show_notification(f" Usuário '{nome}' adicionado.", "success")
        except Exception:
            pass

        # Se a view da lista expuser um método `refresh`, chamá-lo
        list_widget = self.loaded_views.get('UsuariosView')
        if list_widget and hasattr(list_widget, 'refresh'):
            try:
                list_widget.refresh()
            except Exception:
                pass

        # Alternar para a aba de lista (índice 1)
        try:
            self._select(1)
        except Exception:
            pass

    def add_view(self, widget: QWidget, title: str = ""):
        """Adiciona uma view manualmente ao stack"""
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {MILK_BG};
                color: {DARK_TEXT};
            }}
        """)
        self.stack.addWidget(widget)
        
    def show_notification(self, message: str, type: str = "info", duration: int = 3000):
        """Exibe uma notificação temporária"""
        from PyQt5.QtWidgets import QLabel
        
        # Criar label de notificação
        notification = QLabel(message, self)
        
        # Estilo baseado no tipo
        if type == "success":
            bg_color = GREEN_SUCCESS
        elif type == "error":
            bg_color = RED_ERROR
        elif type == "warning":
            bg_color = ORANGE_ALERT
        else:
            bg_color = TEAL_PRIMARY
            
        notification.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 14px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13.5px;
                margin: 10px;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        # Posicionar no canto superior direito
        notification.adjustSize()
        notification.move(self.width() - notification.width() - 30, 100)  # Abaixo da barra de menu
        notification.show()
        
        # Animação de entrada
        notification.setWindowOpacity(0)
        anim = QPropertyAnimation(notification, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()
        
        # Timer para remover
        QTimer.singleShot(duration, lambda: self._fade_out_notification(notification))
    
    def _fade_out_notification(self, notification: QLabel):
        """Remove a notificação com animação de fade out"""
        anim = QPropertyAnimation(notification, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.finished.connect(notification.deleteLater)
        anim.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Estilo global da aplicação (tema leite)
    app.setStyleSheet(f"""
        /* Estilo geral */
        QWidget {{
            font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            background-color: {MILK_BG};
        }}
        
        /* Janela principal */
        QMainWindow {{
            background-color: {MILK_BG};
        }}
        
        /* Botões */
        QPushButton {{
            background-color: {LIGHT_CARD};
            color: {DARK_TEXT};
            border: 1px solid {LIGHT_BORDER};
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 13.5px;
            transition: all 0.2s ease;
        }}
        QPushButton:hover {{
            background-color: {LIGHT_HOVER};
            border-color: {TEAL_PRIMARY};
            transform: translateY(-1px);
            box-shadow: 0px 3px 8px rgba(0,0,0,0.05);
        }}
        QPushButton:pressed {{
            background-color: {TEAL_PRIMARY};
            color: white;
            transform: translateY(0px);
        }}
        
        /* Campos de entrada */
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: white;
            color: {DARK_TEXT};
            border: 1px solid {LIGHT_BORDER};
            padding: 10px 14px;
            border-radius: 8px;
            selection-background-color: {TEAL_PRIMARY};
            font-size: 13.5px;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {TEAL_PRIMARY};
            border-width: 2px;
            box-shadow: 0px 0px 0px 3px {TEAL_PRIMARY}15;
        }}
        
        /* Labels */
        QLabel {{
            color: {DARK_TEXT};
        }}
        
        /* Tabelas */
        QTableView, QTableWidget {{
            background-color: white;
            border: 1px solid {LIGHT_BORDER};
            border-radius: 8px;
            gridline-color: {LIGHT_BORDER};
            font-size: 13px;
            alternate-background-color: {MILK_BG};
        }}
        QHeaderView::section {{
            background-color: {LIGHT_HOVER};
            color: {DARK_TEXT};
            padding: 12px;
            border: none;
            border-right: 1px solid {LIGHT_BORDER};
            border-bottom: 1px solid {LIGHT_BORDER};
            font-weight: 600;
            font-size: 12.5px;
        }}
        
        /* Abas */
        QTabWidget::pane {{
            border: 1px solid {LIGHT_BORDER};
            border-radius: 8px;
            background-color: white;
            margin-top: 5px;
        }}
        QTabBar::tab {{
            background-color: {LIGHT_CARD};
            color: {GRAY_TEXT};
            padding: 12px 24px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background-color: white;
            color: {TEAL_PRIMARY};
            border-bottom: 3px solid {TEAL_PRIMARY};
        }}
        QTabBar::tab:hover {{
            background-color: {LIGHT_HOVER};
            color: {DARK_TEXT};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {LIGHT_HOVER};
            width: 12px;
            border-radius: 6px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background-color: #C1C8D1;
            border-radius: 6px;
            min-height: 25px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {TEAL_PRIMARY};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        /* GroupBox */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {LIGHT_BORDER};
            border-radius: 10px;
            margin-top: 12px;
            padding-top: 18px;
            background-color: white;
            color: {DARK_TEXT};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 10px 0 10px;
            color: {TEAL_PRIMARY};
            font-size: 13.5px;
        }}
        
        /* Checkbox e RadioButton */
        QCheckBox, QRadioButton {{
            spacing: 10px;
            color: {DARK_TEXT};
            font-size: 13.5px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {LIGHT_BORDER};
        }}
        QCheckBox::indicator:checked {{
            background-color: {TEAL_PRIMARY};
            border: 1px solid {TEAL_PRIMARY};
            image: url();
        }}
        QRadioButton::indicator:checked {{
            background-color: {TEAL_PRIMARY};
            border: 5px solid white;
            border-radius: 9px;
        }}
        
        /* Cards e containers */
        QFrame[frameShape="4"] {{ /* QFrame::StyledPanel */
            background-color: white;
            border: 1px solid {LIGHT_BORDER};
            border-radius: 10px;
            padding: 15px;
        }}
    """)
    
    w = UsuarioPage()
    w.resize(1400, 900)
    w.setWindowTitle("Kamba Farma - Gestão de Usuários")
    
    # Ícone da janela (opcional)
    try:
        from PyQt5.QtGui import QIcon
        w.setWindowIcon(QIcon.fromTheme("system-users"))
    except:
        pass
    
    w.show()
    sys.exit(app.exec_())