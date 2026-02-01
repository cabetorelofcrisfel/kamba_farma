from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QStackedWidget, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

# Ensure imports work similarly to AdminDashboard
src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_root not in sys.path:
    sys.path.insert(0, src_root)

# Reuse VendaPage and ProdutosView when possible
from models.admindashboard.venda import VendaPage

try:
    from models.admindashboard.produto.produtos_view import ProdutosView
except Exception:
    try:
        from models.admindashboard.produto import ProdutoPage as ProdutosView
    except Exception:
        ProdutosView = None


class PerfilPage(QWidget):
    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user or {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Perfil do Utilizador")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        layout.addWidget(title)

        nome = QLabel(f"Nome: {self.current_user.get('nome', self.current_user.get('username', '---'))}")
        perfil = QLabel(f"Perfil: {self.current_user.get('perfil', self.current_user.get('role', 'user'))}")
        layout.addWidget(nome)
        layout.addWidget(perfil)
        layout.addStretch()


class UserDashboard(QMainWindow):
    def __init__(self, current_user: dict | None = None):
        super().__init__()
        self.current_user = current_user or {}
        self.setWindowTitle('User Dashboard - Kamba Farma')
        self.resize(1100, 700)

        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # side menu
        menu = QWidget()
        menu.setFixedWidth(220)
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(8, 8, 8, 8)

        header = QLabel('Kamba Farma')
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet('font-weight:700; font-size:18px;')
        menu_layout.addWidget(header)

        # user info
        ulabel = QLabel(self.current_user.get('nome', self.current_user.get('username', 'Usuário')))
        ulabel.setStyleSheet('font-size:13px;')
        menu_layout.addWidget(ulabel)

        # buttons
        self.btn_venda = QPushButton('💸 Venda')
        self.btn_catalogo = QPushButton('📦 Catálogo')
        self.btn_perfil = QPushButton('👤 Perfil')
        for b in (self.btn_venda, self.btn_catalogo, self.btn_perfil):
            b.setCursor(Qt.PointingHandCursor)
            b.setCheckable(True)
            b.setMinimumHeight(40)
            menu_layout.addWidget(b)

        menu_layout.addStretch()

        # content stack
        self.stack = QStackedWidget()
        # Venda
        try:
            self.venda_page = VendaPage()
        except Exception:
            self.venda_page = QLabel('Venda page missing')
        # Catalogo
        if ProdutosView is not None:
            try:
                self.catalogo_page = ProdutosView()
            except Exception:
                self.catalogo_page = QLabel('Catálogo page error')
        else:
            self.catalogo_page = QLabel('Catálogo não disponível')
        # Perfil
        self.perfil_page = PerfilPage(current_user=self.current_user)

        self.stack.addWidget(self.venda_page)
        self.stack.addWidget(self.catalogo_page)
        self.stack.addWidget(self.perfil_page)

        main_layout.addWidget(menu)
        main_layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        # connections
        self.btn_venda.clicked.connect(lambda: self._select(0))
        self.btn_catalogo.clicked.connect(lambda: self._select(1))
        self.btn_perfil.clicked.connect(lambda: self._select(2))

        self.btn_venda.setChecked(True)
        self._select(0)

    def _select(self, idx: int):
        for b in (self.btn_venda, self.btn_catalogo, self.btn_perfil):
            b.setChecked(False)
        if idx == 0:
            self.btn_venda.setChecked(True)
        elif idx == 1:
            self.btn_catalogo.setChecked(True)
        else:
            self.btn_perfil.setChecked(True)
        if 0 <= idx < self.stack.count():
            self.stack.setCurrentIndex(idx)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = UserDashboard(current_user={'nome':'Teste','perfil':'user'})
    w.show()
    sys.exit(app.exec_())
