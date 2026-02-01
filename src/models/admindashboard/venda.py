"""SPA container for vendas views.

Provides `VendaPage` which dynamically loads views from the `venda/`
subfolder. Expected view files and class names (defaults):

- vender_produto.py -> `VenderProdutoView`
- devolucao_de_produto.py -> `DevolucaoDeProdutoView`
- historico_de_venda.py -> `HistoricoDeVendaView`

If a view file is missing or doesn't expose the expected class, a
user-friendly placeholder is shown with instructions.
"""

from pathlib import Path
import importlib.util
import sys
from typing import Optional, TYPE_CHECKING

# Tornar import acessível para analisadores de tipo (pylance/mypy) sem importar em tempo de
# execução. Isso evita avisos "could not be resolved" no editor enquanto a importação dinâmica
# continua funcionando em runtime.
if TYPE_CHECKING:
    from models.admindashboard.venda.historico_de_venda import HistoricoVendaView  # type: ignore

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget,
    QLabel, QApplication, QFrame
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt5.QtGui import QFont


# Theme colors (light)
BG = "#FBFCFE"
CARD = "#FFFFFF"
BORDER = "#E6EEF8"
TEXT = "#162029"
ACCENT = "#2563EB"
MUTED = "#6B7280"


def _load_view_from_path(path: Path, class_name: str) -> Optional[QWidget]:
    """Import `class_name` from `path` and return an instance, or None."""
    try:
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        mod_name = f"_venda_dynamic_{path.stem}"
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
        cls = getattr(module, class_name, None)
        if cls is None:
            return None
        return cls()
    except Exception:
        return None


class VendaPage(QWidget):
    """SPA container for venda-related views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.views_dir = Path(__file__).parent / "venda"
        self._setup_ui()
        self.setStyleSheet(f"""
            QWidget {{ background-color: {BG}; color: {TEXT}; font-family: 'Segoe UI', Arial; }}
            QPushButton {{ border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; }}
            QPushButton:checked {{ background-color: {ACCENT}20; color: {ACCENT}; border: 1px solid {ACCENT}; }}
        """)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top menu
        menu = QFrame()
        menu.setFixedHeight(80)
        menu.setStyleSheet(f"background-color: {CARD}; border-bottom: 1px solid {BORDER};")
        menu_layout = QHBoxLayout(menu)
        menu_layout.setContentsMargins(20, 10, 20, 10)
        menu_layout.setSpacing(8)

        title = QLabel("🛒 GESTÃO DE VENDAS")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {TEXT}; padding-right: 16px; border-right: 1px solid {BORDER};")
        menu_layout.addWidget(title)

        # Buttons
        self.btn_vender = QPushButton("💸 Vender Produto")
        self.btn_devolver = QPushButton("↩️ Devolver Produto")
        self.btn_historico = QPushButton("📜 Histórico de Vendas")

        for btn in (self.btn_vender, self.btn_devolver, self.btn_historico):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setMinimumWidth(160)
            menu_layout.addWidget(btn)

        menu_layout.addStretch()

        # Status
        status = QLabel("Sistema de Vendas")
        status.setStyleSheet(f"color: {MUTED}; padding: 8px 12px; background: {BG}; border-radius: 8px;")
        menu_layout.addWidget(status)

        main_layout.addWidget(menu)

        # Content area
        content = QFrame()
        content.setStyleSheet(f"background-color: {BG};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self._load_views()

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content, 1)

        # Connections
        self.btn_vender.clicked.connect(lambda: self._select(0))
        self.btn_devolver.clicked.connect(lambda: self._select(1))
        self.btn_historico.clicked.connect(lambda: self._select(2))

        self.btn_vender.setChecked(True)

    def _select(self, index: int):
        buttons = [self.btn_vender, self.btn_devolver, self.btn_historico]
        for i, b in enumerate(buttons):
            b.setChecked(i == index)
        # Caso especial: se selecionar Histórico (index 2), tentar carregar dinamicamente a view
        if index == 2:
            try:
                import importlib
                # tentar importar como pacote primeiro
                try:
                    import models.admindashboard.venda.historico_de_venda as hist_mod
                    importlib.reload(hist_mod)
                except ModuleNotFoundError:
                    # fallback: carregar diretamente pelo caminho
                    historico_path = Path(__file__).parent / 'venda' / 'historico_de_venda.py'
                    if historico_path.exists():
                        import importlib.util
                        spec = importlib.util.spec_from_file_location('models.admindashboard.venda.historico_de_venda', str(historico_path))
                        hist_mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(hist_mod)
                    else:
                        raise

                HistClass = getattr(hist_mod, 'HistoricoVendaView', None)
                if HistClass:
                    old_widget = self.stack.widget(2) if 2 < self.stack.count() else None
                    new_widget = HistClass()
                    if old_widget is not None:
                        self.stack.removeWidget(old_widget)
                        try:
                            old_widget.deleteLater()
                        except Exception:
                            pass
                    self.stack.insertWidget(2, new_widget)
                    self.stack.setCurrentIndex(2)
                    return
            except Exception as e:
                try:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, 'Erro', f'Falha ao carregar Histórico de Vendas: {e}')
                except Exception:
                    print('Falha ao carregar Histórico de Vendas:', e)
                # Se falhar, continua com o comportamento padrão abaixo

        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            anim = QPropertyAnimation(self.stack, b"windowOpacity")
            anim.setDuration(220)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()

    def _load_views(self):
        """Load vender, devolver and historico views from venda/"""
        views = [
            (self.views_dir / "vender_produto.py", "VenderProdutoView"),
            (self.views_dir / "devolucao_de_produto.py", "DevolucaoDeProdutoView"),
            (self.views_dir / "historico_de_venda.py", "HistoricoDeVendaView"),
        ]

        for path, class_name in views:
            widget = _load_view_from_path(path, class_name)
            if widget is None:
                placeholder = QWidget()
                placeholder.setStyleSheet(f"background-color: {CARD}; border: 2px dashed {BORDER}; border-radius: 12px;")
                pl = QVBoxLayout(placeholder)
                pl.setContentsMargins(40, 40, 40, 40)
                pl.setAlignment(Qt.AlignCenter)
                label = QLabel(
                    f"<div style='text-align:center'><h3 style='color:{ACCENT};'>{class_name}</h3>"
                    f"<p style='color:{MUTED}; max-width:520px;'>Crie {path.name} na pasta venda/ com uma classe <b>{class_name}</b> que herde de QWidget.</p></div>"
                )
                label.setWordWrap(True)
                pl.addWidget(label)
                self.stack.addWidget(placeholder)
            else:
                # Wrap in container to give margins
                container = QWidget()
                cl = QVBoxLayout(container)
                cl.setContentsMargins(0, 0, 0, 0)
                cl.addWidget(widget)
                self.stack.addWidget(container)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = VendaPage()
    w.resize(1200, 900)
    w.setWindowTitle('Kamba Farma - Vendas')
    w.show()
    sys.exit(app.exec_())