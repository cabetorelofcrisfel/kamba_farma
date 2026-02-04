"""View principal de usuários.

Exporta `UsuariosView`, um QWidget com lista de usuários,
campo de pesquisa e ações básicas.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QToolButton, QSizePolicy,
    QMenu, QAction, QProgressBar, QSplitter, QGroupBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QBrush, QColor, QPixmap, QPainter, QPainterPath

# Paleta de cores - TEMA CLARO
LIGHT_BG = "#FFFFFF"
LIGHT_CARD = "#F6F6F6"
LIGHT_BORDER = "#DADADA"
LIGHT_HOVER = "#F0F0F0"
TEXT_COLOR = "#000000"
GRAY_TEXT = "#6B6B6B"
TEAL_PRIMARY = "#00BFA5"
TEAL_DARK = "#00897B"
GREEN_SUCCESS = "#4CAF50"
RED_ERROR = "#F44336"
PURPLE = "#9C27B0"
BLUE_INFO = "#2196F3"
ORANGE_ALERT = "#FF9800"

# Backwards-compatible aliases (many stylesheets use the old dark-theme names)
DARK_BG = LIGHT_BG
DARK_CARD = LIGHT_CARD
DARK_BORDER = LIGHT_BORDER
DARK_HOVER = LIGHT_HOVER
WHITE_TEXT = TEXT_COLOR


class UsuarioCard(QFrame):
    """Card individual para exibir informações de um usuário."""
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario = usuario_data
        self._setup_ui()
        
    def _setup_ui(self):
        self.setObjectName("usuarioCard")
        self.setMinimumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        # Cabeçalho do card
        header_layout = QHBoxLayout()
        
        # Ícone/avatar
        avatar_label = QLabel()
        avatar_label.setFixedSize(40, 40)
        avatar_label.setStyleSheet(f"""
            background-color: {TEAL_PRIMARY};
            border-radius: 20px;
            color: {WHITE_TEXT};
            font-weight: bold;
            font-size: 14px;
            qproperty-alignment: AlignCenter;
        """)
        
        # Iniciais do nome ou foto se disponível
        nome = self.usuario.get('nome', 'U')
        foto_bytes = self.usuario.get('foto')
        if foto_bytes:
            try:
                pix = QPixmap()
                # sqlite may return memoryview/bytes
                if isinstance(foto_bytes, memoryview):
                    foto_bytes = foto_bytes.tobytes()
                pix.loadFromData(foto_bytes)

                size = avatar_label.width()
                # scale to cover then crop to a circle
                pix = pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

                result = QPixmap(size, size)
                result.fill(Qt.transparent)

                painter = QPainter(result)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, size, size)
                painter.setClipPath(path)
                # draw the scaled pixmap filling the result
                painter.drawPixmap(0, 0, pix)
                painter.end()

                avatar_label.setPixmap(result)
                avatar_label.setScaledContents(False)
                avatar_label.setStyleSheet("background-color: transparent; border-radius: 20px;")
            except Exception:
                # fallback to initials
                partes = nome.split()
                if len(partes) >= 2:
                    iniciais = f"{partes[0][0]}{partes[-1][0]}".upper()
                else:
                    iniciais = nome[0].upper() if nome else "U"
                avatar_label.setText(iniciais)
        else:
            partes = nome.split()
            if len(partes) >= 2:
                iniciais = f"{partes[0][0]}{partes[-1][0]}".upper()
            else:
                iniciais = nome[0].upper() if nome else "U"
            avatar_label.setText(iniciais)
        
        # Informações principais
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)
        
        nome_label = QLabel(nome)
        nome_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {WHITE_TEXT};
        """)
        
        email = self.usuario.get('email', '')
        email_label = QLabel(f"📧 {email}" if email else "📧 Sem email")
        email_label.setStyleSheet(f"""
            font-size: 12px;
            color: {GRAY_TEXT};
        """)
        
        info_layout.addWidget(nome_label)
        info_layout.addWidget(email_label)
        
        # Status
        status = "✅ ATIVO" if self.usuario.get('ativo', 1) == 1 else "⏸️ INATIVO"
        status_label = QLabel(status)
        status_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 10px;
            background-color: {'#4CAF5020' if self.usuario.get('ativo', 1) == 1 else '#F4433620'};
            color: {'#4CAF50' if self.usuario.get('ativo', 1) == 1 else '#F44336'};
            qproperty-alignment: AlignCenter;
        """)
        status_label.setFixedWidth(80)
        
        header_layout.addWidget(avatar_label)
        header_layout.addWidget(info_widget, 1)
        header_layout.addWidget(status_label)
        
        # Detalhes
        details_widget = QWidget()
        details_layout = QHBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(20)
        
        # Informações adicionais
        info_items = [
            ("👤", "Username:", self.usuario.get('username', 'N/A')),
            ("🎭", "Cargo:", self._traduzir_cargo(self.usuario.get('perfil', 'user'))),
            ("📅", "Cadastro:", self._formatar_data(self.usuario.get('criado_em', 'N/A'))),
        ]
        
        for icon, label, value in info_items:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(2)
            
            label_text = QLabel(f"{icon} {label}")
            label_text.setStyleSheet(f"""
                font-size: 10px;
                color: {GRAY_TEXT};
            """)
            
            value_text = QLabel(value)
            value_text.setStyleSheet(f"""
                font-size: 12px;
                color: {WHITE_TEXT};
                font-weight: 500;
            """)
            
            item_layout.addWidget(label_text)
            item_layout.addWidget(value_text)
            details_layout.addWidget(item_widget)
        
        details_layout.addStretch()
        
        # Botões de ação
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(5)
        
        # Botões com ícones
        actions = [
            ("✏️", "Editar", self._on_editar),
            ("🔄", "Atualizar", self._on_atualizar),
            ("🗑️", "Remover", self._on_remover),
            ("👁️", "Ver", self._on_ver),
        ]
        
        for icon, tooltip, callback in actions:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DARK_BORDER};
                    color: {GRAY_TEXT};
                    border: none;
                    border-radius: 6px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {TEAL_PRIMARY};
                    color: {WHITE_TEXT};
                }}
            """)
            actions_layout.addWidget(btn)
        
        layout.addLayout(header_layout)
        layout.addWidget(details_widget)
        layout.addWidget(actions_widget)
        
        # Aplicar estilo do card
        self.setStyleSheet(f"""
            #usuarioCard {{
                background-color: {DARK_CARD};
                border: 1px solid {DARK_BORDER};
                border-radius: 10px;
            }}
            #usuarioCard:hover {{
                border-color: {TEAL_PRIMARY};
                background-color: {DARK_HOVER};
            }}
        """)
    
    def _traduzir_cargo(self, perfil):
        """Traduz o código do perfil para nome amigável."""
        traducoes = {
            'admin': 'Administrador',
            'farmaceutico': 'Farmacêutico',
            'caixa': 'Operador de Caixa',
            'gerente': 'Gerente',
            'user': 'Usuário'
        }
        return traducoes.get(perfil, perfil.capitalize())
    
    def _formatar_data(self, data_str):
        """Formata a data para exibição."""
        if data_str == 'N/A':
            return data_str
        
        try:
            # Tentar vários formatos de data
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(data_str, fmt)
                    return dt.strftime("%d/%m/%Y")
                except:
                    continue
        except:
            pass
        
        return data_str
    
    def _on_editar(self):
        """Abre edição do usuário."""
        QMessageBox.information(self, "Editar", 
            f"Editar usuário: {self.usuario.get('nome', 'N/A')}")
    
    def _on_atualizar(self):
        """Atualiza informações do usuário."""
        QMessageBox.information(self, "Atualizar", 
            f"Atualizar usuário: {self.usuario.get('nome', 'N/A')}")
    
    def _on_remover(self):
        """Remove o usuário."""
        QMessageBox.information(self, "Remover", 
            f"Remover usuário: {self.usuario.get('nome', 'N/A')}")
    
    def _on_ver(self):
        """Visualiza detalhes do usuário."""
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Detalhes - {self.usuario.get('nome', 'Usuário')}")
        layout = QVBoxLayout(dlg)

        # Foto ampliada (renderizada circularmente)
        foto_label = QLabel()
        foto_label.setAlignment(Qt.AlignCenter)
        foto_label.setFixedSize(160, 160)
        foto_bytes = self.usuario.get('foto')
        if foto_bytes:
            try:
                if isinstance(foto_bytes, memoryview):
                    foto_bytes = foto_bytes.tobytes()
                pix = QPixmap()
                pix.loadFromData(foto_bytes)

                size = foto_label.width()
                pix = pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

                result = QPixmap(size, size)
                result.fill(Qt.transparent)

                painter = QPainter(result)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, size, size)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pix)
                painter.end()

                foto_label.setPixmap(result)
                foto_label.setStyleSheet("background-color: transparent; border-radius: 80px;")
            except Exception:
                foto_label.setText("Sem foto disponível")
        else:
            foto_label.setText("Sem foto disponível")

        layout.addWidget(foto_label)

        # Informação textual
        info = QLabel()
        info.setText(
            f"<b>Nome:</b> {self.usuario.get('nome', 'N/A')}<br/>"
            f"<b>Email:</b> {self.usuario.get('email', 'N/A')}<br/>"
            f"<b>Username:</b> {self.usuario.get('username', 'N/A')}<br/>"
            f"<b>Perfil:</b> {self._traduzir_cargo(self.usuario.get('perfil', 'user'))}<br/>"
            f"<b>Cadastro:</b> {self._formatar_data(self.usuario.get('criado_em', 'N/A'))}"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Botões
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        dlg.exec_()


class UsuariosView(QWidget):
    """Lista de usuários com ações básicas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = self._get_db_path()
        self.usuarios = []
        self._setup_ui()
        self.carregar_usuarios()

    def _get_db_path(self):
        """Obtém o caminho do banco de dados."""
        # Preferir função centralizada de localização do DB quando disponível
        try:
            from src.config.paths import DB_DIR
            from database.db import get_db_path
            db_path = get_db_path(DB_DIR)
            if db_path.exists():
                return str(db_path)
        except Exception:
            pass

        # Fallback: tenta encontrar o DB relativo à raiz do projeto (4 pais do arquivo)
        possible_paths = [
            Path(__file__).parents[4] / 'database' / 'kamba_farma.db',  # project root/database
            Path(__file__).parents[3] / 'database' / 'kamba_farma.db',
            Path(__file__).parents[2] / 'database' / 'kamba_farma.db',
            Path(__file__).parents[1] / 'database' / 'kamba_farma.db',
            Path(__file__).parent / 'kamba_farma.db',
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        return str(Path(__file__).parent / 'usuarios_demo.db')

    def _setup_ui(self):
        """Configura a interface do usuário."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Cabeçalho
        header_widget = self._criar_cabecalho()
        main_layout.addWidget(header_widget)

        # Barra de ferramentas
        toolbar_widget = self._criar_toolbar()
        main_layout.addWidget(toolbar_widget)

        # Container para cards/lista
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(15)
        
        # Scroll area para os cards
        scroll_widget = QFrame()
        scroll_widget.setObjectName("scrollWidget")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(self.cards_container)
        scroll_layout.addStretch()
        
        main_layout.addWidget(scroll_widget, 1)

        # Barra de status
        status_widget = self._criar_barra_status()
        main_layout.addWidget(status_widget)

        # Aplicar estilo
        self._aplicar_estilo()

    def _criar_cabecalho(self):
        """Cria o cabeçalho da página."""
        widget = QFrame()
        widget.setObjectName("cabecalho")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Título e descrição
        texto_widget = QWidget()
        texto_layout = QVBoxLayout(texto_widget)
        texto_layout.setContentsMargins(0, 0, 0, 0)
        texto_layout.setSpacing(5)
        
        titulo = QLabel("👥 GERENCIAMENTO DE USUÁRIOS")
        titulo.setObjectName("titulo")
        titulo.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {TEAL_PRIMARY};
        """)
        
        descricao = QLabel("Visualize, gerencie e edite todos os usuários do sistema")
        descricao.setObjectName("descricao")
        descricao.setStyleSheet(f"""
            font-size: 13px;
            color: {GRAY_TEXT};
        """)
        
        texto_layout.addWidget(titulo)
        texto_layout.addWidget(descricao)
        
        # Estatísticas
        stats_widget = QFrame()
        stats_widget.setObjectName("statsWidget")
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(15)
        
        stats = [
            ("📊", "Total:", "0"),
            ("✅", "Ativos:", "0"),
            ("👑", "Admins:", "0"),
            ("🔄", "Hoje:", "0"),
        ]
        
        for icon, label, valor in stats:
            stat = QWidget()
            stat_layout = QVBoxLayout(stat)
            stat_layout.setContentsMargins(0, 0, 0, 0)
            stat_layout.setSpacing(2)
            
            label_widget = QLabel(f"{icon} {label}")
            label_widget.setStyleSheet(f"""
                font-size: 11px;
                color: {GRAY_TEXT};
                font-weight: 600;
            """)
            
            valor_widget = QLabel(valor)
            valor_widget.setObjectName(f"valor_{label.replace(':', '').lower()}")
            valor_widget.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {WHITE_TEXT};
            """)
            
            stat_layout.addWidget(label_widget)
            stat_layout.addWidget(valor_widget)
            stats_layout.addWidget(stat)
        
        layout.addWidget(texto_widget)
        layout.addStretch()
        layout.addWidget(stats_widget)

        return widget

    def _criar_toolbar(self):
        """Cria a barra de ferramentas."""
        widget = QFrame()
        widget.setObjectName("toolbar")
        widget.setFixedHeight(70)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)

        # Busca
        busca_widget = QWidget()
        busca_layout = QHBoxLayout(busca_widget)
        busca_layout.setContentsMargins(0, 0, 0, 0)
        busca_layout.setSpacing(10)
        
        self.input_search = QLineEdit()
        self.input_search.setObjectName("inputSearch")
        self.input_search.setPlaceholderText("🔍 Buscar por nome, email ou username...")
        self.input_search.setMinimumHeight(40)
        self.input_search.setMinimumWidth(300)
        self.input_search.textChanged.connect(self._on_search)
        
        # Botão de busca avançada
        btn_avancada = QPushButton("⚙️")
        btn_avancada.setToolTip("Busca avançada")
        btn_avancada.setFixedSize(40, 40)
        btn_avancada.setCursor(Qt.PointingHandCursor)
        
        busca_layout.addWidget(self.input_search)
        busca_layout.addWidget(btn_avancada)
        
        # Filtros
        filtros_widget = QWidget()
        filtros_layout = QHBoxLayout(filtros_widget)
        filtros_layout.setContentsMargins(0, 0, 0, 0)
        filtros_layout.setSpacing(10)
        
        # Filtro por status
        self.filtro_status = QComboBox()
        self.filtro_status.setObjectName("filtroStatus")
        self.filtro_status.addItems(["📋 Todos", "✅ Ativos", "⏸️ Inativos"])
        self.filtro_status.setMinimumHeight(40)
        self.filtro_status.setMinimumWidth(120)
        self.filtro_status.currentIndexChanged.connect(self._filtrar_usuarios)
        
        # Filtro por cargo
        self.filtro_cargo = QComboBox()
        self.filtro_cargo.setObjectName("filtroCargo")
        self.filtro_cargo.addItems(["👔 Todos os cargos", "👑 Administrador", "💊 Farmacêutico", "💰 Caixa", "👤 Usuário"])
        self.filtro_cargo.setMinimumHeight(40)
        self.filtro_cargo.setMinimumWidth(150)
        self.filtro_cargo.currentIndexChanged.connect(self._filtrar_usuarios)
        
        filtros_layout.addWidget(self.filtro_status)
        filtros_layout.addWidget(self.filtro_cargo)
        
        layout.addWidget(busca_widget)
        layout.addWidget(filtros_widget)
        layout.addStretch()
        
        # Botões de ação
        acoes_widget = QWidget()
        acoes_layout = QHBoxLayout(acoes_widget)
        acoes_layout.setContentsMargins(0, 0, 0, 0)
        acoes_layout.setSpacing(10)
        
        botoes = [
            ("🔄 ATUALIZAR", self._on_refresh, BLUE_INFO),
        ]
        
        for texto, funcao, cor in botoes:
            btn = QPushButton(texto)
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(funcao)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor};
                    color: {WHITE_TEXT};
                    border: none;
                    border-radius: 6px;
                    padding: 0 20px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {cor}DD;
                }}
            """)
            acoes_layout.addWidget(btn)
        
        layout.addWidget(acoes_widget)

        return widget

    def _criar_barra_status(self):
        """Cria a barra de status."""
        widget = QFrame()
        widget.setObjectName("statusBar")
        widget.setFixedHeight(50)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Informação de resultados
        self.status_label = QLabel("Carregando usuários...")
        self.status_label.setStyleSheet(f"""
            font-size: 12px;
            color: {GRAY_TEXT};
            font-weight: 600;
        """)
        
        # Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {DARK_BORDER};
                border-radius: 4px;
                background-color: {DARK_BG};
            }}
            QProgressBar::chunk {{
                background-color: {TEAL_PRIMARY};
                border-radius: 3px;
            }}
        """)
        
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.progress_bar)

        return widget

    def _aplicar_estilo(self):
        """Aplica o estilo à interface."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {DARK_BG};
                color: {WHITE_TEXT};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            #cabecalho {{
                background-color: transparent;
            }}
            
            #toolbar, #statusBar {{
                background-color: {DARK_CARD};
                border-radius: 8px;
                border: 1px solid {DARK_BORDER};
            }}
            
            #statsWidget {{
                background-color: {DARK_CARD};
                border-radius: 8px;
                padding: 10px;
                border: 1px solid {DARK_BORDER};
            }}
            
            QLineEdit, QComboBox {{
                background-color: {DARK_BG};
                color: {WHITE_TEXT};
                border: 1px solid {DARK_BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: {TEAL_PRIMARY};
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border-color: {TEAL_PRIMARY};
            }}
            
            QLineEdit::placeholder {{
                color: {GRAY_TEXT}80;
            }}
            
            QComboBox::drop-down {{
                border: none;
                background-color: {DARK_BORDER};
                border-radius: 0 6px 6px 0;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {GRAY_TEXT};
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {DARK_CARD};
                color: {WHITE_TEXT};
                selection-background-color: {TEAL_PRIMARY};
                border: 1px solid {DARK_BORDER};
            }}
            
            #scrollWidget {{
                background-color: transparent;
                border: none;
            }}
        """)

    def carregar_usuarios(self):
        """Carrega os usuários do banco de dados."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(usuarios)")
            colunas = [row['name'] for row in cursor.fetchall()]
            
            # Construir query baseada nas colunas disponíveis
            campos = ['id', 'nome', 'email', 'username', 'perfil', 'ativo', 'criado_em']
            campos_disponiveis = [c for c in campos if c in colunas]
            
            if not campos_disponiveis:
                campos_disponiveis = ['id', 'nome']
                
            query = f"SELECT {', '.join(campos_disponiveis)} FROM usuarios ORDER BY id DESC"
            cursor.execute(query)
            
            self.usuarios = []
            for row in cursor.fetchall():
                usuario = dict(row)
                # Garantir campos padrão
                usuario['email'] = usuario.get('email', '')
                usuario['username'] = usuario.get('username', f"user{usuario['id']}")
                    # foto pode ser bytes ou None
                usuario['foto'] = usuario.get('foto', None)
                usuario['perfil'] = usuario.get('perfil', 'user')
                usuario['ativo'] = usuario.get('ativo', 1)
                usuario['criado_em'] = usuario.get('criado_em', 'N/A')
                self.usuarios.append(usuario)
            
            conn.close()
            self.atualizar_cards()
            
        except sqlite3.Error as e:
            self._mostrar_erro("Erro ao conectar ao banco de dados", str(e))
            # Carregar dados de demonstração
            self.carregar_dados_demo()

    def carregar_dados_demo(self):
        """Carrega dados de demonstração."""
        self.usuarios = [
            {
                'id': 1, 'nome': 'Administrador Sistema', 'email': 'admin@kambafarma.com',
                'username': 'admin', 'perfil': 'admin', 'ativo': 1,
                'criado_em': '2024-01-15 10:30:00'
            },
            {
                'id': 2, 'nome': 'Maria Silva', 'email': 'maria@kambafarma.com',
                'username': 'maria.s', 'perfil': 'farmaceutico', 'ativo': 1,
                'criado_em': '2024-02-10 09:15:00'
            },
            {
                'id': 3, 'nome': 'João Santos', 'email': 'joao@kambafarma.com',
                'username': 'joao.s', 'perfil': 'caixa', 'ativo': 1,
                'criado_em': '2024-02-28 14:00:00'
            },
            {
                'id': 4, 'nome': 'Ana Oliveira', 'email': 'ana@kambafarma.com',
                'username': 'ana.o', 'perfil': 'gerente', 'ativo': 0,
                'criado_em': '2024-03-05 11:45:00'
            },
            {
                'id': 5, 'nome': 'Carlos Mendes', 'email': 'carlos@kambafarma.com',
                'username': 'carlos.m', 'perfil': 'user', 'ativo': 1,
                'criado_em': '2024-03-12 08:20:00'
            },
        ]
        self.atualizar_cards()

    def atualizar_cards(self):
        """Atualiza os cards de usuários."""
        # Limpar cards existentes
        for i in reversed(range(self.cards_layout.count())): 
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Adicionar novos cards
        for usuario in self.usuarios:
            card = UsuarioCard(usuario)
            self.cards_layout.addWidget(card)
        
        # Atualizar estatísticas
        self.atualizar_estatisticas()

    def atualizar_estatisticas(self):
        """Atualiza as estatísticas no cabeçalho."""
        total = len(self.usuarios)
        ativos = sum(1 for u in self.usuarios if u.get('ativo') == 1)
        admins = sum(1 for u in self.usuarios if u.get('perfil') == 'admin')
        
        # Atualizar labels
        for widget in self.findChildren(QLabel):
            if widget.objectName() == "valor_total":
                widget.setText(str(total))
            elif widget.objectName() == "valor_ativos":
                widget.setText(str(ativos))
            elif widget.objectName() == "valor_admins":
                widget.setText(str(admins))
            elif widget.objectName() == "valor_hoje":
                # Contar cadastros de hoje (simulado)
                widget.setText("1")
        
        # Atualizar status
        self.status_label.setText(f"📊 Mostrando {total} usuário(s)")

    def _on_search(self):
        """Realiza busca nos usuários."""
        termo = self.input_search.text().lower()
        self._filtrar_usuarios()

    def _filtrar_usuarios(self):
        """Filtra os usuários com base nos critérios."""
        termo = self.input_search.text().lower()
        filtro_status = self.filtro_status.currentText()
        filtro_cargo = self.filtro_cargo.currentText()
        
        # Limpar cards existentes
        for i in reversed(range(self.cards_layout.count())): 
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Filtrar usuários
        usuarios_filtrados = []
        for usuario in self.usuarios:
            # Filtro por busca
            if termo:
                campos_busca = [
                    usuario.get('nome', '').lower(),
                    usuario.get('email', '').lower(),
                    usuario.get('username', '').lower()
                ]
                if not any(termo in campo for campo in campos_busca):
                    continue
            
            # Filtro por status
            if filtro_status == "✅ Ativos" and usuario.get('ativo') != 1:
                continue
            elif filtro_status == "⏸️ Inativos" and usuario.get('ativo') != 0:
                continue
            
            # Filtro por cargo
            if filtro_cargo != "👔 Todos os cargos":
                cargo_esperado = filtro_cargo.split()[-1].lower()
                perfil = usuario.get('perfil', 'user')
                
                # Mapear tradução
                mapeamento = {
                    'administrador': 'admin',
                    'farmacêutico': 'farmaceutico',
                    'caixa': 'caixa',
                    'usuário': 'user'
                }
                
                if cargo_esperado in mapeamento and perfil != mapeamento[cargo_esperado]:
                    continue
            
            usuarios_filtrados.append(usuario)
        
        # Adicionar cards filtrados
        for usuario in usuarios_filtrados:
            card = UsuarioCard(usuario)
            self.cards_layout.addWidget(card)
        
        # Atualizar status
        self.status_label.setText(f"📊 Mostrando {len(usuarios_filtrados)} de {len(self.usuarios)} usuário(s)")

    def _on_add(self):
        """Adiciona um novo usuário."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Adicionar")
        msg.setText("Abrir formulário de adicionar usuário")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {DARK_CARD};
                color: {WHITE_TEXT};
            }}
            QMessageBox QLabel {{
                color: {WHITE_TEXT};
            }}
        """)
        msg.exec_()

    def _on_edit(self):
        """Edita o usuário selecionado."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Editar")
        msg.setText("Abrir edição do usuário selecionado")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {DARK_CARD};
                color: {WHITE_TEXT};
            }}
            QMessageBox QLabel {{
                color: {WHITE_TEXT};
            }}
        """)
        msg.exec_()

    def _on_refresh(self):
        """Atualiza a lista de usuários."""
        self.progress_bar.setValue(30)
        self.carregar_usuarios()
        self.progress_bar.setValue(100)
        
        # Resetar progresso após um tempo
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.progress_bar.setValue(0))
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Atualizar")
        msg.setText("Lista de usuários atualizada!")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {DARK_CARD};
                color: {WHITE_TEXT};
            }}
            QMessageBox QLabel {{
                color: {WHITE_TEXT};
            }}
        """)
        msg.exec_()

    def _on_relatorio(self):
        """Gera relatório de usuários."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Relatório")
        msg.setText("Gerar relatório de usuários")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {DARK_CARD};
                color: {WHITE_TEXT};
            }}
            QMessageBox QLabel {{
                color: {WHITE_TEXT};
            }}
        """)
        msg.exec_()

    def _on_exportar(self):
        """Exporta lista de usuários."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Exportar")
        msg.setText("Exportar lista de usuários")
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {DARK_CARD};
                color: {WHITE_TEXT};
            }}
            QMessageBox QLabel {{
                color: {WHITE_TEXT};
            }}
        """)
        msg.exec_()

    def _mostrar_erro(self, titulo, mensagem):
        """Exibe uma mensagem de erro estilizada."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensagem)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {DARK_CARD};
                color: {WHITE_TEXT};
            }}
            QMessageBox QLabel {{
                color: {WHITE_TEXT};
            }}
        """)
        msg.exec_()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = UsuariosView()
    window.setWindowTitle("Gerenciamento de Usuários - Kamba Farma")
    window.resize(1200, 800)
    window.show()
    
    sys.exit(app.exec_())