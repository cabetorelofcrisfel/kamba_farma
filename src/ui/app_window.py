from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTabWidget,
    QPushButton,
    QListWidget,
)
from PyQt5.QtWidgets import QLineEdit, QMessageBox

from core.session import Session
from services.usuario_service import authenticate


class MainWindow(QMainWindow):
    def __init__(self, initial_tab: int = 0, current_user: dict = None):
        super().__init__()
        self.setWindowTitle('Kamba Farma')
        self.resize(1000, 700)

        self.session = Session()
        if current_user:
            self.session.login(current_user)

        tabs = QTabWidget()
        tabs.addTab(self._login_tab(), 'Login')
        tabs.addTab(self._dashboard_tab(), 'Dashboard')
        tabs.addTab(self._produtos_tab(), 'Produtos')
        tabs.addTab(self._vendas_tab(), 'Vendas')
        tabs.addTab(self._fornecedores_tab(), 'Fornecedores')
        tabs.addTab(self._usuarios_tab(), 'Utilizadores')

        self.setCentralWidget(tabs)
        # selecionar a aba inicial (por defeito: Login)
        try:
            tabs.setCurrentIndex(initial_tab)
        except Exception:
            pass

    def _placeholder_tab(self, text: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout()
        label = QLabel(text)
        label.setStyleSheet('font-size:16px; padding:12px')
        l.addWidget(label)
        w.setLayout(l)
        return w

    def _login_tab(self):
        w = QWidget()
        l = QVBoxLayout()

        title = QLabel('Login')
        title.setStyleSheet('font-weight:600; font-size:18px')
        l.addWidget(title)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText('Nome de utilizador')
        l.addWidget(self.input_username)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText('Password')
        self.input_password.setEchoMode(QLineEdit.Password)
        l.addWidget(self.input_password)

        btn_login = QPushButton('Entrar')
        btn_login.clicked.connect(self._handle_login)
        l.addWidget(btn_login)

        w.setLayout(l)
        return w

    def _handle_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()
        if not username or not password:
            QMessageBox.warning(self, 'Erro', 'Por favor preencha todos os campos')
            return

        user = authenticate(username, password)
        if not user:
            QMessageBox.warning(self, 'Erro', 'Credenciais inválidas')
            return

        self.session.login(user)
        role = user.get('role', 'user')

        if role == 'admin':
            target_index = 5
        else:
            target_index = 3

        tabs_widget = self.centralWidget()
        if isinstance(tabs_widget, QTabWidget):
            tabs_widget.setCurrentIndex(target_index)

    def _dashboard_tab(self):
        # Mostrar dashboard diferente conforme o papel do utilizador
        user = getattr(self.session, 'user', None)
        if user and user.get('role') == 'admin':
            return self._placeholder_tab('Dashboard Administrativo — acesso de administrador')
        return self._placeholder_tab('Dashboard do Utilizador — acesso restrito de funcionário')

    def _produtos_tab(self):
        w = QWidget()
        l = QVBoxLayout()

        title = QLabel('Produtos')
        title.setStyleSheet('font-weight:600; font-size:18px')
        l.addWidget(title)

        produtos_list = QListWidget()
        produtos_list.addItem('Produto exemplo 1')
        produtos_list.addItem('Produto exemplo 2')
        l.addWidget(produtos_list)

        btn_add = QPushButton('Adicionar produto (placeholder)')
        l.addWidget(btn_add)

        w.setLayout(l)
        return w

    def _vendas_tab(self):
        return self._placeholder_tab('Vendas — esta aba ainda está em desenvolvimento')

    def _fornecedores_tab(self):
        return self._placeholder_tab('Fornecedores — em desenvolvimento')

    def _usuarios_tab(self):
        return self._placeholder_tab('Utilizadores — em desenvolvimento')

