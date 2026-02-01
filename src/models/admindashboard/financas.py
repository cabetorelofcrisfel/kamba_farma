"""
Finanças SPA - carrega as views de entrada/saída financeiras.

Estrutura esperada em `financas/`:
- entrada.py -> classe `EntradaView` (QWidget)
- saida.py  -> classe `SaidaView` (QWidget)

Se as views não existirem, placeholders são exibidos.
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


def _load_view_from_path(path: Path, class_name: str) -> Optional[QWidget]:
    try:
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        mod_name = f"_financas_dynamic_{path.stem}"
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        cls = getattr(module, class_name, None)
        if cls is None:
            return None
        return cls()
    except Exception:
        return None


class FinancasPage(QWidget):
    """Container SPA para o módulo de Finanças."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.views_dir = Path(__file__).parent / "financas"
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top menu
        menu = QFrame()
        menu.setFixedHeight(80)
        menu.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #EEE;")
        menu_layout = QHBoxLayout(menu)
        menu_layout.setContentsMargins(20, 10, 20, 10)
        menu_layout.setSpacing(8)

        title = QLabel("💼 FINANÇAS")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("padding-right:12px;")
        menu_layout.addWidget(title)

        # Buttons
        self.btn_entrada = QPushButton("➕ Entrada")
        self.btn_saida = QPushButton("➖ Saída")
        self.btn_diario = QPushButton("📅 Diário")
        self.btn_balanco = QPushButton("💰 Balanço")
        for btn in (self.btn_entrada, self.btn_saida, self.btn_diario, self.btn_balanco):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setMinimumWidth(140)
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        status = QLabel("Módulo Financeiro")
        status.setStyleSheet("color:#666; padding:6px 10px; background:#F9FAFB; border-radius:6px;")
        menu_layout.addWidget(status)

        main_layout.addWidget(menu)

        # Content area
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.stack = QStackedWidget()
        self._load_views()
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content, 1)

        # Connections
        self.btn_entrada.clicked.connect(lambda: self._select(0))
        self.btn_saida.clicked.connect(lambda: self._select(1))
        self.btn_diario.clicked.connect(lambda: self._select(2))
        self.btn_balanco.clicked.connect(lambda: self._select(3))
        self.btn_entrada.setChecked(True)

    def _select(self, index: int):
        buttons = [self.btn_entrada, self.btn_saida, self.btn_diario, self.btn_balanco]
        for i, b in enumerate(buttons):
            b.setChecked(i == index)
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            anim = QPropertyAnimation(self.stack, b"windowOpacity")
            anim.setDuration(200)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()

    def _load_views(self):
        views = [
            (self.views_dir / "entrada.py", "EntradaView"),
            (self.views_dir / "saida.py", "SaidaView"),
            (self.views_dir / "diario.py", "DiarioView"),
            (self.views_dir / "balanco.py", "BalancoView"),
        ]

        for path, class_name in views:
            widget = _load_view_from_path(path, class_name)
            if widget is None:
                # Placeholder
                placeholder = QWidget()
                placeholder.setStyleSheet("background: #FFFFFF; border: 2px dashed #EEE; border-radius: 8px;")
                pl = QVBoxLayout(placeholder)
                pl.setContentsMargins(40, 40, 40, 40)
                pl.setAlignment(Qt.AlignCenter)
                lbl = QLabel(f"🚧 {class_name} em {path.name} não encontrado\nCrie a view em {path}")
                lbl.setWordWrap(True)
                pl.addWidget(lbl)
                self.stack.addWidget(placeholder)
            else:
                container = QWidget()
                cl = QVBoxLayout(container)
                cl.setContentsMargins(0, 0, 0, 0)
                cl.addWidget(widget)
                self.stack.addWidget(container)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = FinancasPage()
    w.resize(1200, 800)
    w.setWindowTitle('Kamba Farma - Finanças')
    w.show()
    sys.exit(app.exec_())
