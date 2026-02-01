from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QApplication,
    QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
import sys
import sqlite3
from pathlib import Path
import logging

# logging para debug de login (arquivo local)
logger = logging.getLogger('kamba.login')
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    log_dir = Path(__file__).resolve().parents[2] / 'kamba' / 'logs'
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        log_dir = Path(__file__).resolve().parents[2]
    fh = logging.FileHandler(log_dir / 'login_debug.log')
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(fmt)
    logger.addHandler(fh)

try:
    from core.auth import hash_password
except Exception:
    try:
        from src.core.auth import hash_password
    except Exception:
        def hash_password(p):
            import hashlib
            return hashlib.sha256(p.encode('utf-8')).hexdigest()
# Não ligar à base de dados por enquanto — autenticação local de teste

# Adicione estas cores se precisar de constantes
AZUL_CARRREGADO = "#1e3a8a"      # Azul escuro para textos e destaques
AZUL_BEBE = "#93c5fd"           # Azul claro para fundos e hover
VERDE_PRINCIPAL = "#10b988"     # Verde predominante não muito carregado
CINZA_ESCURO = "#374151"        # Para textos
CINZA_CLARO = "#f3f4f6"         # Para fundos
BRANCO = "#ffffff"

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login - Kamba Farma')
        # Tamanho inicial, permitir redimensionamento/maximização
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # Remover bordas da janela para usar barra de título customizada
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        # Widget central com barra de título customizada
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Barra de título customizada (botões minim/max/fechar)
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 6, 8, 6)
        title_layout.setSpacing(6)
        title_layout.addStretch()

        self.btn_minimize = QPushButton("—")
        self.btn_maximize = QPushButton("▢")
        self.btn_close = QPushButton("✕")

        for b in (self.btn_minimize, self.btn_maximize, self.btn_close):
            b.setFixedSize(36, 26)
            b.setCursor(Qt.PointingHandCursor)
            b.setFlat(True)
            title_layout.addWidget(b)

        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_maximize.clicked.connect(self.toggle_maximize_restore)
        self.btn_close.clicked.connect(self.close)

        outer_layout.addWidget(title_bar)

        # Área de conteúdo (mantém o layout HBox original)
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        outer_layout.addWidget(content_widget, 1)
        
        # Painel esquerdo (imagem/decoração)
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo/Título no painel esquerdo
        logo_label = QLabel("KAMBA FARMA")
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_label)
        
        # Imagem decorativa (substitua por uma imagem real se tiver)
        image_label = QLabel()
        image_label.setPixmap(QPixmap(500, 400))  # Placeholder
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet(f"background-color: {AZUL_BEBE}; border-radius: 20px;")
        left_layout.addWidget(image_label)
        
        # Espaçador
        left_layout.addStretch()
        
        # Texto de rodapé no painel esquerdo
        footer_label = QLabel("© Kamba Farma - Sistema Farmacêutico")
        footer_label.setObjectName("footerLabel")
        footer_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(footer_label)
        
        # Painel direito (formulário de login)
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_panel.setMinimumWidth(500)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 60, 60, 60)
        right_layout.setSpacing(30)
        
        # Cabeçalho do formulário
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)
        
        welcome_label = QLabel("Bem-vindo de volta")
        welcome_label.setObjectName("welcomeLabel")
        welcome_label.setAlignment(Qt.AlignCenter)
        
        self.subtitle_label = QLabel("Faça login para acessar o sistema")
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Botões de seleção de perfil (Sou Usuário / Sou Admin)
        role_widget = QWidget()
        role_layout = QHBoxLayout(role_widget)
        role_layout.setContentsMargins(0, 0, 0, 0)
        role_layout.setSpacing(10)
        
        self.btn_role_user = QPushButton("Sou Usuário")
        self.btn_role_user.setObjectName("roleButtonUser")
        self.btn_role_user.setCheckable(True)
        self.btn_role_user.setCursor(Qt.PointingHandCursor)
        self.btn_role_user.clicked.connect(lambda: self.set_role_selection('user'))
        
        self.btn_role_admin = QPushButton("Sou Admin")
        self.btn_role_admin.setObjectName("roleButtonAdmin")
        self.btn_role_admin.setCheckable(True)
        self.btn_role_admin.setCursor(Qt.PointingHandCursor)
        self.btn_role_admin.clicked.connect(lambda: self.set_role_selection('admin'))
        
        role_layout.addStretch()
        role_layout.addWidget(self.btn_role_user)
        role_layout.addWidget(self.btn_role_admin)
        role_layout.addStretch()
        
        header_layout.addStretch()
        header_layout.addWidget(welcome_label)
        header_layout.addWidget(self.subtitle_label)
        header_layout.addWidget(role_widget)
        header_layout.addStretch()
        
        # Formulário
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(25)
        
        # Campo de usuário
        user_widget = QWidget()
        user_layout = QVBoxLayout(user_widget)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(8)
        
        user_label = QLabel("Nome de utilizador")
        user_label.setObjectName("inputLabel")
        
        self.input_username = QLineEdit()
        self.input_username.setObjectName("usernameInput")
        self.input_username.setPlaceholderText("Digite seu nome de usuário")
        self.input_username.setMinimumHeight(50)
        
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.input_username)
        
        # Campo de senha
        password_widget = QWidget()
        password_layout = QVBoxLayout(password_widget)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)
        
        password_label = QLabel("Senha")
        password_label.setObjectName("inputLabel")
        
        self.input_password = QLineEdit()
        self.input_password.setObjectName("passwordInput")
        self.input_password.setPlaceholderText("Digite sua senha")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setMinimumHeight(50)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.input_password)
        
        # Botões
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(15)
        
        self.btn_login = QPushButton("Entrar no Sistema")
        self.btn_login.setObjectName("loginButton")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setMinimumHeight(55)
        self.btn_login.clicked.connect(self.handle_login)
        
        self.btn_forgot = QPushButton("Esqueceu a senha?")
        self.btn_forgot.setObjectName("forgotButton")
        self.btn_forgot.setCursor(Qt.PointingHandCursor)
        self.btn_forgot.setMinimumHeight(40)
        self.btn_forgot.clicked.connect(self.handle_forgot)
        
        buttons_layout.addWidget(self.btn_login)
        buttons_layout.addWidget(self.btn_forgot)
        
        # Adicionar widgets ao formulário
        form_layout.addWidget(user_widget)
        form_layout.addWidget(password_widget)
        form_layout.addWidget(buttons_widget)
        
        # Adicionar tudo ao layout direito
        right_layout.addWidget(header_widget)
        right_layout.addWidget(form_widget)
        right_layout.addStretch()
        
        # Adicionar painéis ao layout principal (conteúdo)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Aplicar estilo
        self.apply_stylesheet()
        
        # Configurar animação de hover nos botões
        self.setup_animations()
        
        # Conectar tecla Enter ao login
        self.input_password.returnPressed.connect(self.handle_login)
        self.input_username.returnPressed.connect(self.handle_login)
        
        # Focar no campo de usuário
        QTimer.singleShot(100, self.input_username.setFocus)
        # Seleção de perfil padrão
        try:
            self.set_role_selection('user')
        except Exception:
            pass
        # indica se o login foi validado contra o banco de dados
        self._db_authenticated = False

    def apply_stylesheet(self):
        style = f"""
            /* Janela principal */
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {AZUL_CARRREGADO}, stop:1 #0f766e);
            }}
            
            /* Painel esquerdo */
            #leftPanel {{
                background-color: {BRANCO};
                border-radius: 0px;
            }}
            
            #logoLabel {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 42px;
                font-weight: 800;
                color: {VERDE_PRINCIPAL};
                margin-bottom: 40px;
                line-height: 1.2;
            }}
            
            #footerLabel {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                color: {CINZA_ESCURO};
                opacity: 0.7;
            }}
            
            /* Painel direito */
            #rightPanel {{
                background-color: {BRANCO};
                border-radius: 20px 0px 0px 20px;
            }}
            
            /* Labels do cabeçalho */
            #welcomeLabel {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 32px;
                font-weight: 700;
                color: {CINZA_ESCURO};
            }}
            
            #subtitleLabel {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                color: #6b7280;
                font-weight: 400;
            }}
            
            /* Labels dos campos */
            #inputLabel {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                color: {CINZA_ESCURO};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            /* Campos de entrada */
            QLineEdit {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                padding: 0px 20px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                background-color: {CINZA_CLARO};
                color: {CINZA_ESCURO};
                selection-background-color: {VERDE_PRINCIPAL};
            }}
            
            QLineEdit:focus {{
                border: 2px solid {VERDE_PRINCIPAL};
                background-color: {BRANCO};
            }}
            
            QLineEdit#usernameInput, QLineEdit#passwordInput {{
                font-size: 15px;
            }}
            
            /* Botão de login */
            #loginButton {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: 600;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {VERDE_PRINCIPAL}, stop:1 #059669);
                border: none;
                border-radius: 12px;
                padding: 10px;
                margin-top: 10px;
            }}
            
            #loginButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0da271, stop:1 #047857);
            }}
            
            #loginButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #065f46);
            }}
            
            /* Botão de esqueci senha */
            #forgotButton {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: {AZUL_CARRREGADO};
                background: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-weight: 500;
            }}
            
            #forgotButton:hover {{
                background-color: {AZUL_BEBE}40;
                color: {AZUL_CARRREGADO};
            }}
            
            #forgotButton:pressed {{
                background-color: {AZUL_BEBE}60;
            }}

            /* Botões de seleção de perfil */
            QPushButton#roleButtonUser, QPushButton#roleButtonAdmin {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                color: {CINZA_ESCURO};
                background: transparent;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px 14px;
                min-width: 120px;
                font-weight: 600;
            }}

            QPushButton#roleButtonUser:checked, QPushButton#roleButtonAdmin:checked {{
                color: white;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {VERDE_PRINCIPAL}, stop:1 #059669);
                border: none;
            }}
            
            /* Placeholder text */
            QLineEdit::placeholder {{
                color: #9ca3af;
                font-weight: 400;
            }}
        """
        self.setStyleSheet(style)
        
        # Configurar fontes específicas
        font_title = QFont("Segoe UI", 42, QFont.Bold)
        font_welcome = QFont("Segoe UI", 32, QFont.Bold)
        font_input = QFont("Segoe UI", 15)
        font_button = QFont("Segoe UI", 16, QFont.DemiBold)
        # Ajustes de estilo para a barra de título e botões
        extra_style = """
            #titleBar {
                background: transparent;
            }
            #titleBar QPushButton {
                border: none;
                color: #374151;
                font-weight: 700;
                background: transparent;
            }
            #titleBar QPushButton:hover {
                background-color: #f3f4f6;
                border-radius: 4px;
            }
        """
        self.setStyleSheet(self.styleSheet() + extra_style)

    def setup_animations(self):
        """Configurar animações para os botões"""
        pass  # Podemos adicionar animações mais complexas se necessário

    def set_role_selection(self, role: str):
        """Define o perfil selecionado ('user' ou 'admin') e atualiza a UI.
        Também preenche o campo de usuário com um valor de conveniência.
        """
        self.selected_role = role
        if role == 'admin':
            self.btn_role_admin.setChecked(True)
            self.btn_role_user.setChecked(False)
            try:
                # Não preencher automaticamente o campo de usuário
                self.input_username.clear()
            except Exception:
                pass
            try:
                self.subtitle_label.setText("Entrando como Admin — insira sua senha")
            except Exception:
                pass
        else:
            self.btn_role_user.setChecked(True)
            self.btn_role_admin.setChecked(False)
            try:
                # Não preencher automaticamente o campo de usuário
                self.input_username.clear()
            except Exception:
                pass
            try:
                self.subtitle_label.setText("Entrando como Usuário — insira sua senha")
            except Exception:
                pass

    def toggle_maximize_restore(self):
        """Alterna entre maximizar e restaurar a janela."""
        if self.isMaximized():
            self.showNormal()
            try:
                self.btn_maximize.setText("▢")
            except Exception:
                pass
        else:
            self.showMaximized()
            try:
                self.btn_maximize.setText("❐")
            except Exception:
                pass

    def handle_forgot(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Recuperação de Senha")
        msg.setText("Solicitação enviada com sucesso!")
        msg.setInformativeText("Um link de recuperação foi enviado para o seu e-mail cadastrado.")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {BRANCO};
                font-family: 'Segoe UI', Arial;
            }}
            QLabel {{
                color: {CINZA_ESCURO};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {VERDE_PRINCIPAL};
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #0da271;
            }}
        """)
        msg.exec_()

    def handle_login(self):
        # Adicionar efeito visual durante o login
        original_text = self.btn_login.text()
        self.btn_login.setText("Verificando...")
        self.btn_login.setEnabled(False)
        
        username = self.input_username.text().strip()
        password = self.input_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, 'Campos obrigatórios', 
                'Por favor, preencha todos os campos.')
            self.btn_login.setText(original_text)
            self.btn_login.setEnabled(True)
            return
        
        # Primeiro: autenticação local para desenvolvimento
        local_users = {
            'admin': {'password': 'admin', 'role': 'admin'},
            'func': {'password': 'func', 'role': 'user'},
        }
        entry = local_users.get(username)
        user = None
        if entry and password == entry['password']:
            user = {'username': username, 'role': entry['role']}
            self._db_authenticated = False

        # Se não for usuário local, tentar autenticar contra a base de dados
        if not user:
            # resolver caminho do DB a partir de config, fallback para busca
            try:
                from config.settings import DB_FILE
                db_path = DB_FILE
            except Exception:
                # subir até encontrar pasta `database`
                file_path = Path(__file__).resolve()
                _ROOT = file_path
                for _ in range(8):
                    if (_ROOT / 'database').exists():
                        break
                    _ROOT = _ROOT.parent
                db_path = _ROOT / 'database' / 'kamba_farma.db'

            try:
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                logger.debug("Login attempt username=%r db_path=%s", username, db_path)
                cur.execute("SELECT id, nome, senha_hash, perfil, ativo FROM usuarios WHERE nome = ? COLLATE NOCASE LIMIT 1", (username,))
                row = cur.fetchone()
                if not row:
                    # Fallback: allow entering 'admin' to match perfil='admin'
                    cur.execute("SELECT id, nome, senha_hash, perfil, ativo FROM usuarios WHERE perfil = ? COLLATE NOCASE LIMIT 1", (username,))
                    row = cur.fetchone()
                conn.close()

                if not row:
                    logger.debug("User not found (by name or profile): %r", username)
                    self.shake_login_button()
                    QMessageBox.warning(self, 'Falha no login', 'Credenciais inválidas. Verifique usuário/senha.')
                    self.btn_login.setText(original_text)
                    self.btn_login.setEnabled(True)
                    return

                if row['ativo'] == 0:
                    QMessageBox.warning(self, 'Conta inativa', 'Este usuário está inativo. Contate o administrador.')
                    self.btn_login.setText(original_text)
                    self.btn_login.setEnabled(True)
                    return

                # verificar hash
                h = hash_password(password)
                logger.debug("Comparing hashes for %r: given=%s stored=%s", username, h, row['senha_hash'])
                if h != row['senha_hash']:
                    logger.debug("Hash mismatch for user %r", username)
                    self.shake_login_button()
                    QMessageBox.warning(self, 'Falha no login', 'Credenciais inválidas. Verifique usuário/senha.')
                    self.btn_login.setText(original_text)
                    self.btn_login.setEnabled(True)
                    return

                role_val = row['perfil'] if row['perfil'] is not None else row.get('perfil', 'user') if hasattr(row, 'get') else (row['perfil'] if row['perfil'] is not None else 'user')
                # sqlite3.Row doesn't implement .get reliably, use explicit fallback
                if role_val is None:
                    role_val = 'user'
                user = {'username': row['nome'], 'role': role_val, 'id': row['id']}
                self._db_authenticated = True

            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao acessar o banco de dados: {e}')
                self.btn_login.setText(original_text)
                self.btn_login.setEnabled(True)
                return
        role = user.get('role', 'user')
        # Usamos a aba 'Dashboard' (índice 1) e o conteúdo muda conforme o role
        initial_tab = 1
        # guardar utilizador autenticado para passar à MainWindow
        self.authenticated_user = user
        
        # Transição suave para a próxima janela
        self.btn_login.setText("Login bem-sucedido!")
        QTimer.singleShot(800, lambda: self.open_main_window())

    def shake_login_button(self):
        """Animação de shake para feedback de erro"""
        import random
        original_pos = self.btn_login.pos()
        for i in range(0, 6):
            x = original_pos.x() + random.randint(-5, 5)
            y = original_pos.y()
            self.btn_login.move(x, y)
            QApplication.processEvents()
            QTimer.singleShot(50, lambda: None)
        self.btn_login.move(original_pos)

    def open_main_window(self):
        """Abre a janela apropriada após login (AdminDashboard para admin)."""
        # If authenticated against DB, always open UserDashboard
        if getattr(self, '_db_authenticated', False):
            try:
                from models.userdashboard.dashboarduser import UserDashboard
                self.main = UserDashboard(current_user=self.authenticated_user)
            except Exception:
                # fallback to admin dashboard if user dashboard missing
                from models.admindashboard.dashboardadmin import AdminDashboard
                self.main = AdminDashboard(current_user=self.authenticated_user)
            self.main.showFullScreen()
            self.close()
            return

        # otherwise follow role-based behavior (local/dev users)
        role = self.authenticated_user.get('role')
        if role == 'admin':
            from models.admindashboard.dashboardadmin import AdminDashboard
            self.main = AdminDashboard(current_user=self.authenticated_user)
        else:
            try:
                from models.userdashboard.dashboarduser import UserDashboard
                self.main = UserDashboard(current_user=self.authenticated_user)
            except Exception:
                try:
                    from ui.app_window import MainWindow
                    self.main = MainWindow(initial_tab=1, current_user=self.authenticated_user)
                except Exception:
                    from models.admindashboard.dashboardadmin import AdminDashboard
                    self.main = AdminDashboard(current_user=self.authenticated_user)

        self.main.showFullScreen()
        self.close()

    def keyPressEvent(self, event):
        """Capturar teclas especiais"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo mais moderno
    
    # Configurar paleta de cores global
    palette = app.palette()
    palette.setColor(palette.Window, QColor(BRANCO))
    palette.setColor(palette.WindowText, QColor(CINZA_ESCURO))
    palette.setColor(palette.Base, QColor(CINZA_CLARO))
    palette.setColor(palette.AlternateBase, QColor(AZUL_BEBE))
    palette.setColor(palette.ToolTipBase, QColor(VERDE_PRINCIPAL))
    palette.setColor(palette.ToolTipText, QColor(BRANCO))
    palette.setColor(palette.Text, QColor(CINZA_ESCURO))
    palette.setColor(palette.Button, QColor(VERDE_PRINCIPAL))
    palette.setColor(palette.ButtonText, QColor(BRANCO))
    palette.setColor(palette.BrightText, QColor(BRANCO))
    palette.setColor(palette.Link, QColor(AZUL_CARRREGADO))
    palette.setColor(palette.Highlight, QColor(VERDE_PRINCIPAL))
    palette.setColor(palette.HighlightedText, QColor(BRANCO))
    app.setPalette(palette)
    
    # Criar e exibir janela (abrir em tela cheia)
    login_window = LoginWindow()
    login_window.showFullScreen()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()