"""
Lightweight Single-Page Application loader for produto/* views.

This file provides `ProdutoPage`, a small SPA container that dynamically
loads widget classes from files in the `produto/` subfolder. Missing
views are represented by placeholders so the UI remains runnable.
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
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath

from config.colors import *
# Local aliases and helpers
MILK_BG = BACKGROUND_GRAY
CARD_BG = WHITE
LIGHT_BORDER = "#E8E8E8"
ACCENT_BORDER = PRIMARY_DARK
TEXT_PRIMARY = TEXT_PRIMARY
TEXT_SECONDARY = "#7F8C8D"
TEXT_LIGHT = "#95A5A6"
TEAL_PRIMARY = PRIMARY_COLOR
TEAL_LIGHT = "#E6F9FB"
TEAL_HOVER = "#CFF8FA"
GREEN_SUCCESS = "#2ECC71"
RED_ERROR = ACCENT_RED
PURPLE = "#9B59B6"
BLUE_INFO = "#3498DB"
ORANGE_ALERT = "#F39C12"
SHADOW_COLOR = SHADOW_COLOR

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


class ModernButton(QPushButton):
    """Botão moderno com efeitos."""
    def __init__(self, text="", icon="", parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.base_color = TEAL_PRIMARY
        self.is_selected = False
        self.setText(f"{icon} {text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(45)
        self.setMinimumWidth(160)
        self._update_style()
        
    def setSelected(self, selected):
        self.is_selected = selected
        self._update_style()
        
    def _update_style(self):
        if self.is_selected:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {TEAL_PRIMARY};
                    color: white;
                    border: 2px solid {TEAL_PRIMARY};
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: {TEAL_PRIMARY}DD;
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px {TEAL_PRIMARY}40;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CARD_BG};
                    color: {TEXT_SECONDARY};
                    border: 1px solid {LIGHT_BORDER};
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background-color: {TEAL_LIGHT};
                    color: {TEAL_PRIMARY};
                    border-color: {TEAL_PRIMARY};
                    transform: translateY(-1px);
                }}
            """)


def _load_view_from_path(path: Path, class_name: str) -> Optional[QWidget]:
    """Import `class_name` from `path` and return an instance, or None."""
    try:
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        mod_name = f"_produto_dynamic_{path.stem}"
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        cls = getattr(module, class_name, None)
        if cls is None:
            return None
        return cls()
    except Exception:
        return None


class ProdutoPage(QWidget):
    """SPA container for produto-related views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.views_dir = Path(__file__).parent / "produto"
        self._setup_ui()
        self._apply_modern_styles()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(0)
        
        # Configurar fundo leitoso
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(MILK_BG))
        self.setPalette(palette)

        # Barra superior de navegação horizontal
        nav_bar = self._create_navigation_bar()
        main_layout.addWidget(nav_bar)

        # Área de conteúdo - StackedWidget
        content_frame = RoundedFrame(radius=12)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {MILK_BG};
                border: none;
                border-radius: 12px;
            }}
        """)
        self._load_views()
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_frame, 1)

    def _create_navigation_bar(self):
        """Cria a barra de navegação horizontal."""
        nav_frame = QFrame()
        # Aumentado para proporcionar mais espaço visual no topo
        nav_frame.setFixedHeight(130)
        nav_frame.setStyleSheet(f"""
            background-color: {CARD_BG};
            border-radius: 12px;
            border: 1px solid {LIGHT_BORDER};
            margin-bottom: 15px;
        """)
        
        nav_layout = QVBoxLayout(nav_frame)
        # Margens aumentadas para combinar com a altura do frame
        nav_layout.setContentsMargins(30, 20, 30, 20)
        nav_layout.setSpacing(10)

        

        # Botões de navegação horizontal
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        # Criar botões
        self.btn_adicionar = ModernButton("Adicionar", "")
        self.btn_lista = ModernButton("Lista", "")
        self.btn_catalogo = ModernButton("Catálogo", "")
        self.btn_relatorios = ModernButton("Relatórios", "")
        self.btn_exportar = ModernButton("Exportar", "")
        self.btn_destaques = ModernButton("Destaques", "⭐")

        # Configurar botões
        self.buttons = [
            self.btn_adicionar, self.btn_lista, self.btn_catalogo,
            self.btn_relatorios, self.btn_exportar, self.btn_destaques
        ]
        
        for i, btn in enumerate(self.buttons):
            btn.clicked.connect(lambda checked, idx=i: self._select(idx))
            button_layout.addWidget(btn)

        button_layout.addStretch()
        
        # Status indicator
        status_widget = QFrame()
        status_widget.setStyleSheet(f"""
            background-color: {TEAL_LIGHT};
            border-radius: 8px;
            border: 1px solid {TEAL_PRIMARY}40;
            padding: 5px 15px;
        """)
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"""
            font-size: 12px;
            color: {GREEN_SUCCESS};
        """)
        
        status_label = QLabel("Sistema Ativo")
        status_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {TEXT_SECONDARY};
        """)
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_label)
        status_layout.addSpacing(5)
        
        button_layout.addWidget(status_widget)
        nav_layout.addWidget(button_frame)

        # Selecionar primeiro item
        self.btn_adicionar.setSelected(True)

        return nav_frame

    def _select(self, index: int):
        """Seleciona a view pelo índice"""
        for i, btn in enumerate(self.buttons):
            btn.setSelected(i == index)
        
        if 0 <= index < self.stack.count():
            # Animar transição
            self.stack.setProperty("opacity", 0.0)
            anim = QPropertyAnimation(self.stack, b"windowOpacity")
            anim.setDuration(250)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()
            
            self.stack.setCurrentIndex(index)

    def _load_views(self):
        """Carrega dinamicamente todas as views"""
        views = [
            (self.views_dir / "adicionarproduto_view.py", "AddProductPage"),
            (self.views_dir / "produtos_view.py", "ProdutosView"),
            (self.views_dir / "catalogo_view.py", "CatalogoView"),
            (self.views_dir / "relatorio_view.py", "SalesReportPage"),
            (self.views_dir / "exportarlista_view.py", "ExportListPage"),
            (self.views_dir / "gerir_destaque_view.py", "ManageHighlightPage"),
        ]

        for path, class_name in views:
            widget = _load_view_from_path(path, class_name)
            if widget is None:
                # Criar placeholder estilizado se a view não existir
                placeholder = QWidget()
                placeholder.setStyleSheet(f"""
                    background-color: {CARD_BG};
                    border-radius: 12px;
                    border: 2px dashed {LIGHT_BORDER};
                """)
                
                placeholder_layout = QVBoxLayout(placeholder)
                placeholder_layout.setContentsMargins(40, 40, 40, 40)
                placeholder_layout.setAlignment(Qt.AlignCenter)
                
                placeholder_label = QLabel(
                    f"<div style='text-align: center;'>"
                    f"<h3 style='color:{TEAL_PRIMARY}; margin-bottom: 15px; font-size: 20px;'> View em Construção</h3>"
                    f"<p style='color:{TEXT_SECONDARY}; font-size: 14px; line-height: 1.6; max-width: 500px;'>"
                    f"<b>Classe:</b> {class_name}<br>"
                    f"<b>Arquivo:</b> {path.name}<br><br>"
                    f"Crie este arquivo na pasta <code>produto/</code><br>"
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
                        color: {TEXT_PRIMARY};
                        border-radius: 12px;
                    }}
                """)
                
                # Envolver em um container para margens
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(widget)
                
                self.stack.addWidget(container)

    def _apply_modern_styles(self):
        """Aplica estilos modernos à interface."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {MILK_BG};
                color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
        """)
        
    def show_notification(self, message: str, type: str = "info", duration: int = 3000):
        """Exibe uma notificação temporária."""
        from PyQt5.QtWidgets import QLabel
        
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
        notification.move(self.width() - notification.width() - 30, 120)
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
        QTimer.singleShot(duration, lambda: self._fade_out_notification(notification))
    
    def _fade_out_notification(self, notification):
        """Remove a notificação com animação."""
        anim = QPropertyAnimation(notification, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.finished.connect(notification.deleteLater)
        anim.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Estilo global moderno
    app.setStyleSheet(f"""
        QApplication {{
            background-color: {MILK_BG};
        }}
        
        QScrollBar:vertical {{
            background-color: {MILK_BG};
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {TEXT_LIGHT};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {TEAL_PRIMARY};
        }}
    """)
    
    w = ProdutoPage()
    w.resize(1400, 900)
    w.setWindowTitle("Kamba Farma - Gestão de Produtos")
    
    # Ícone da janela
    try:
        from PyQt5.QtGui import QIcon
        w.setWindowIcon(QIcon.fromTheme("package"))
    except:
        pass
    
    w.show()
    sys.exit(app.exec_())