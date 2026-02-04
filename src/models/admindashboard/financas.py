"""
Finanças SPA - carrega as views de entrada/saída financeiras.

Estrutura esperada em `financas/`:
- entrada.py -> classe `EntradaView` (QWidget)
- saida.py  -> classe `SaidaView` (QWidget)
- diario.py -> classe `DiarioView` (QWidget)
- balanco.py -> classe `BalancoView` (QWidget)

Se as views não existirem, placeholders são exibidos.
"""

from pathlib import Path
import importlib.util
import sys
from typing import Optional, List

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QStackedWidget, QLabel, QFrame, QGraphicsDropShadowEffect,
    QSpacerItem, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QLinearGradient

# Paleta de cores (unificada) - mesma do lote.py
PRIMARY_COLOR = "#28C7D3"
PRIMARY_DARK = "#0A777F"
ACCENT_RED = "#E53935"
BACKGROUND_GRAY = "#F2F2F2"
WHITE = "#FFFFFF"
DARK_GRAY = "#212121"

# Backwards-compatible aliases
SECONDARY_COLOR = "#10B981"
DANGER_COLOR = ACCENT_RED
WARNING_COLOR = "#F59E0B"
BG_COLOR = BACKGROUND_GRAY
CARD_BG = WHITE
BORDER_COLOR = "#E8EEF5"
TEXT_PRIMARY = DARK_GRAY
TEXT_SECONDARY = "#6B7280"
TEXT_LIGHT = "#9CA3AF"
ACCENT_COLOR = "#8B5CF6"
SHADOW_COLOR = "rgba(0, 0, 0, 0.08)"


class RoundedFrame(QFrame):
    """Frame com cantos arredondados e sombra."""
    def __init__(self, radius=16, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Adicionar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        
        painter.fillRect(self.rect(), QColor(CARD_BG))
        
        # Borda suave
        painter.setPen(QColor(BORDER_COLOR))
        painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, self.radius, self.radius)


class ModernNavButton(QPushButton):
    """Botão de navegação moderno."""
    def __init__(self, text="", icon="", parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.is_selected = False
        
        self.setText(f"{icon}  {text}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(48)
        self.setMinimumWidth(160)
        
        # Configurar fonte
        font = QFont("Segoe UI", 11, QFont.Medium)
        self.setFont(font)
        
        self._update_style()
        
    def setSelected(self, selected):
        self.is_selected = selected
        self._update_style()
        
    def _update_style(self):
        if self.is_selected:
            # Botão selecionado
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 {PRIMARY_COLOR}, stop:1 {ACCENT_COLOR});
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 14px 16px;
                    font-size: 13px;
                    font-weight: 600;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #5A7AF9, stop:1 #9D7AF9);
                }}
            """)
        else:
            # Botão normal
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CARD_BG};
                    color: {TEXT_SECONDARY};
                    border: 1.5px solid {BORDER_COLOR};
                    border-radius: 10px;
                    padding: 14px 16px;
                    font-size: 13px;
                    font-weight: 600;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {BG_COLOR};
                    color: {TEXT_PRIMARY};
                    border-color: {PRIMARY_COLOR}40;
                }}
            """)


class HorizontalNavBar(QFrame):
    """Barra de navegação horizontal."""
    itemSelected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # Título da navegação
        title = QLabel(" Navegação")
        title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16px;
            font-weight: 700;
            margin-right: 24px;
        """)
        layout.addWidget(title)
        
        # Botões de navegação
        self.buttons: List[ModernNavButton] = []
        nav_items = [
            ("", "Entrada", "Registrar entradas financeiras"),
            ("", "Saída", "Registrar saídas financeiras"),
            ("", "Diário", "Visualizar diário financeiro"),
            ("", "Balanço", "Visualizar balanço financeiro"),
        ]
        
        for icon, text, tooltip in nav_items:
            btn = ModernNavButton(text, icon)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, idx=len(self.buttons): self._on_item_clicked(idx))
            self.buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Selecionar primeiro item
        if self.buttons:
            self.buttons[0].setSelected(True)
    
    def _on_item_clicked(self, index):
        """Lida com clique em item da navegação."""
        for i, btn in enumerate(self.buttons):
            btn.setSelected(i == index)
        self.itemSelected.emit(index)


class HeaderBar(QFrame):
    """Barra de cabeçalho superior."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        
        # Informações do título
        title_layout = QVBoxLayout()
        title_layout.setSpacing(6)
        
        self.title_label = QLabel("Gestão Financeira")
        title_font = QFont("Segoe UI", 22, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        
        self.subtitle_label = QLabel("Sistema de controle financeiro")
        self.subtitle_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        layout.addStretch()


def _load_view_from_path(path: Path, class_name: str) -> Optional[QWidget]:
    """Dynamically load a QWidget subclass named `class_name` from `path`.
    Returns an instance or None if loading fails.
    """
    try:
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        # Ensure module has a unique name in sys.modules
        mod_name = f"_financas_dynamic_{path.stem}"
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        cls = getattr(module, class_name, None)
        if cls is None:
            return None
        return cls()
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None


class ContentPlaceholder(QWidget):
    """Placeholder estilizado para views não implementadas."""
    def __init__(self, title, filename, classname, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {CARD_BG};
                border-radius: 16px;
                border: 2px dashed {BORDER_COLOR};
            }}
        """)
        
        # Adicionar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setAlignment(Qt.AlignCenter)
        
        # Ícone
        icon = QLabel("")
        icon.setStyleSheet(f"""
            font-size: 72px;
            margin-bottom: 24px;
        """)
        layout.addWidget(icon, 0, Qt.AlignCenter)
        
        # Título
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {TEXT_PRIMARY}; margin-bottom: 12px;")
        layout.addWidget(title_label, 0, Qt.AlignCenter)
        
        # Descrição
        description = QLabel(
            f"<div style='text-align: center; color: {TEXT_PRIMARY}; font-size: 14px; line-height: 1.6;'>"
            f"Esta funcionalidade está em desenvolvimento.<br><br>"
            f"<span style='color: {TEXT_LIGHT}; font-size: 12px;'>"
            f"Para implementar, crie o arquivo:<br>"
            f"<code style='background-color: {PRIMARY_COLOR}; padding: 4px 8px; border-radius: 4px;'>"
            f"financas/{filename}</code><br><br>"
            f"com uma classe chamada<br>"
            f"<code style='background-color: {PRIMARY_COLOR}; padding: 4px 8px; border-radius: 4px;'>"
            f"{classname}</code><br>"
            f"que herde de <code>QWidget</code>."
            f"</span>"
            f"</div>"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Botão de exemplo
        example_btn = QPushButton(" Ver exemplo de código")
        example_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: "#28C7D3";
                color: {PRIMARY_COLOR};
                border: 1.5px solid {PRIMARY_COLOR}40;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                margin-top: 24px;
            }}
            QPushButton:hover {{
                background-color: "#28C7D3";
            }}
        """)
        example_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(example_btn, 0, Qt.AlignCenter)


class FinancasPage(QWidget):
    """Container SPA para o módulo de Finanças."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.views_dir = Path(__file__).parent / "."
        self.setup_ui()

    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Configurar fundo
        self.setAutoFillBackground(True)
        from PyQt5.QtGui import QPalette
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(BG_COLOR))
        self.setPalette(palette)

        # Cabeçalho
        self.header = HeaderBar()
        main_layout.addWidget(self.header)

        # Barra de navegação horizontal
        self.nav_bar = HorizontalNavBar()
        self.nav_bar.itemSelected.connect(self._on_nav_item_selected)
        main_layout.addWidget(self.nav_bar)

        # Área de conteúdo
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background: transparent;
                border: none;
            }
        """)
        
        # Carregar views
        self._load_views()
        
        # Adicionar ao layout
        main_layout.addWidget(self.content_stack, 1)

    def _on_nav_item_selected(self, index):
        """Lida com seleção de item na navegação."""
        self._animate_view_transition(index)
        
        # Atualizar título do cabeçalho
        titles = [
            "Registrar Entradas Financeiras",
            "Registrar Saídas Financeiras",
            "Diário Financeiro",
            "Balanço Financeiro"
        ]
        
        subtitles = [
            "Registre novas entradas financeiras no sistema",
            "Registre novas saídas financeiras no sistema",
            "Visualize o diário completo de movimentações",
            "Visualize o balanço financeiro consolidado"
        ]
        
        if 0 <= index < len(titles):
            self.header.title_label.setText(titles[index])
            self.header.subtitle_label.setText(subtitles[index])

    def _animate_view_transition(self, index):
        """Anima a transição entre views."""
        if index < self.content_stack.count():
            old_widget = self.content_stack.currentWidget()
            new_widget = self.content_stack.widget(index)
            
            if old_widget and new_widget:
                # Configurar animação de fade
                new_widget.setGraphicsEffect(None)
                old_widget.setGraphicsEffect(None)
                
                anim = QPropertyAnimation(old_widget, b"windowOpacity")
                anim.setDuration(200)
                anim.setStartValue(1.0)
                anim.setEndValue(0.0)
                anim.setEasingCurve(QEasingCurve.OutCubic)
                
                anim2 = QPropertyAnimation(new_widget, b"windowOpacity")
                anim2.setDuration(200)
                anim2.setStartValue(0.0)
                anim2.setEndValue(1.0)
                anim2.setEasingCurve(QEasingCurve.OutCubic)
                
                anim.start()
                anim2.start()
                
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(50, lambda: self.content_stack.setCurrentIndex(index))
            else:
                self.content_stack.setCurrentIndex(index)

    def _load_views(self):
        """Load views dynamically or show placeholders."""
        views = [
            ("Entradas Financeiras", "entrada.py", "EntradaView"),
            ("Saídas Financeiras", "saida.py", "SaidaView"),
            ("Diário Financeiro", "diario.py", "DiarioView"),
            ("Balanço Financeiro", "balanco.py", "BalancoView"),
        ]

        for title, filename, classname in views:
            path = self.views_dir / filename
            widget = _load_view_from_path(path, classname)
            
            if widget is None:
                # Criar placeholder estilizado
                placeholder = ContentPlaceholder(title, filename, classname)
                
                # Container para o placeholder
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(placeholder)
                
                self.content_stack.addWidget(container)
            else:
                # Configurar estilo da view carregada
                widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: transparent;
                        color: {TEXT_PRIMARY};
                    }}
                """)
                
                # Container para a view
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(widget)
                
                self.content_stack.addWidget(container)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Estilo global
    app.setStyleSheet(f"""
        * {{
            font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        QScrollBar:vertical {{
            background-color: {BG_COLOR};
            width: 10px;
            border-radius: 5px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {TEXT_LIGHT};
            border-radius: 5px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {PRIMARY_COLOR};
        }}
        
        QScrollBar::add-line, QScrollBar::sub-line {{
            border: none;
            background: none;
        }}
    """)
    
    w = FinancasPage()
    w.setWindowTitle("Sistema de Gestão Financeira - Kamba Farma")
    w.resize(1400, 900)
    w.show()
    
    sys.exit(app.exec_())