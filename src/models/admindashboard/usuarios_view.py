"""View principal de usuários - Versão Simplificada.

Exporta `UsuariosView`, um QWidget com lista de usuários,
campo de pesquisa e ações básicas.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QComboBox, QScrollArea,
    QSizePolicy, QDialog, QDialogButtonBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QFont

from colors import *
# Cores simplificadas
BACKGROUND = WHITE
CARD_BG = "#FFFFFF"
BORDER = "#E0E0E0"
HOVER = "#F5F5F5"
TEXT_PRIMARY = "#212121"
TEXT_SECONDARY = "#757575"
PRIMARY = PRIMARY_COLOR
PRIMARY_LIGHT = "#80CBC4"
ACCENT = ACCENT_RED


class UsuarioCard(QFrame):
    """Card simplificado para exibir informações de um usuário."""
    
    def __init__(self, usuario_data, parent=None):
        super().__init__(parent)
        self.usuario = usuario_data
        self._setup_ui()
        
    def _setup_ui(self):
        self.setObjectName("usuarioCard")
        self.setMinimumHeight(90)
        self.setMaximumHeight(90)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # Avatar circular simples
        avatar_label = QLabel()
        avatar_label.setFixedSize(50, 50)
        
        # Gerar avatar com iniciais
        nome = self.usuario.get('nome', 'U')
        partes = nome.split()
        if len(partes) >= 2:
            iniciais = f"{partes[0][0]}{partes[-1][0]}".upper()
        else:
            iniciais = nome[0].upper() if nome else "U"
        
        avatar_label.setText(iniciais)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet(f"""
            background-color: {PRIMARY};
            color: white;
            border-radius: 25px;
            font-weight: bold;
            font-size: 14px;
        """)
        
        # Informações principais
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        # Nome e status
        nome_widget = QWidget()
        nome_layout = QHBoxLayout(nome_widget)
        nome_layout.setContentsMargins(0, 0, 0, 0)
        nome_layout.setSpacing(8)
        
        nome_label = QLabel(nome)
        nome_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        """)
        
        # Status badge simples
        status = "●" if self.usuario.get('ativo', 1) == 1 else "○"
        status_color = "#4CAF50" if self.usuario.get('ativo', 1) == 1 else "#F44336"
        status_label = QLabel(status)
        status_label.setStyleSheet(f"""
            color: {status_color};
            font-size: 10px;
        """)
        status_label.setToolTip("Ativo" if self.usuario.get('ativo', 1) == 1 else "Inativo")
        
        nome_layout.addWidget(nome_label)
        nome_layout.addWidget(status_label)
        nome_layout.addStretch()
        
        # Email
        email = self.usuario.get('email', '')
        email_label = QLabel(email if email else "Sem email")
        email_label.setStyleSheet(f"""
            font-size: 12px;
            color: {TEXT_SECONDARY};
        """)
        
        # Cargo
        cargo_label = QLabel(self._traduzir_cargo(self.usuario.get('perfil', 'user')))
        cargo_label.setStyleSheet(f"""
            font-size: 11px;
            color: {PRIMARY};
            font-weight: 500;
        """)
        
        info_layout.addWidget(nome_widget)
        info_layout.addWidget(email_label)
        info_layout.addWidget(cargo_label)
        
        layout.addWidget(avatar_label)
        layout.addWidget(info_widget, 1)
        
        # Botão de ações (menu)
        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(30, 30)
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER};
                color: {TEXT_PRIMARY};
            }}
        """)
        menu_btn.clicked.connect(self._mostrar_menu)
        
        layout.addWidget(menu_btn)
        
        # Estilo do card
        self.setStyleSheet(f"""
            #usuarioCard {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            #usuarioCard:hover {{
                border-color: {PRIMARY};
                background-color: {HOVER};
            }}
        """)
    
    def _traduzir_cargo(self, perfil):
        """Traduz o código do perfil para nome amigável."""
        traducoes = {
            'admin': 'Administrador',
            'farmaceutico': 'Farmacêutico',
            'caixa': 'Caixa',
            'gerente': 'Gerente',
            'user': 'Usuário'
        }
        return traducoes.get(perfil, perfil.capitalize())
    
    def _mostrar_menu(self):
        """Mostra menu de ações para o usuário."""
        dlg = QDialog(self)
        dlg.setWindowTitle("Ações")
        dlg.setFixedWidth(200)
        
        layout = QVBoxLayout(dlg)
        layout.setSpacing(5)
        
        nome = self.usuario.get('nome', 'Usuário')
        titulo = QLabel(f"Ações para {nome}")
        titulo.setStyleSheet(f"""
            font-weight: 600;
            color: {TEXT_PRIMARY};
            padding: 10px;
        """)
        layout.addWidget(titulo)
        
        # Botões de ação
        acoes = [
            ("📝 Editar", lambda: self._acao_editar(dlg)),
            ("👁 Ver Detalhes", lambda: self._acao_ver(dlg)),
            ("🔄 Atualizar", lambda: self._acao_atualizar(dlg)),
            ("🗑 Remover", lambda: self._acao_remover(dlg)),
        ]
        
        for texto, funcao in acoes:
            btn = QPushButton(texto)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(funcao)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 4px;
                    color: {TEXT_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {HOVER};
                }}
            """)
            layout.addWidget(btn)
        
        # Botão Cancelar
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setCursor(Qt.PointingHandCursor)
        cancelar_btn.clicked.connect(dlg.reject)
        cancelar_btn.setStyleSheet(f"""
            QPushButton {{
                margin-top: 10px;
                padding: 8px;
                border: 1px solid {BORDER};
                border-radius: 4px;
                color: {TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                background-color: {HOVER};
            }}
        """)
        layout.addWidget(cancelar_btn)
        
        dlg.exec_()
    
    def _acao_editar(self, dlg):
        dlg.accept()
        QMessageBox.information(self, "Editar", f"Editar usuário: {self.usuario.get('nome', 'N/A')}")
    
    def _acao_ver(self, dlg):
        dlg.accept()
        self._mostrar_detalhes()
    
    def _acao_atualizar(self, dlg):
        dlg.accept()
        QMessageBox.information(self, "Atualizar", f"Atualizar usuário: {self.usuario.get('nome', 'N/A')}")
    
    def _acao_remover(self, dlg):
        dlg.accept()
        resposta = QMessageBox.question(self, "Confirmar", 
            f"Tem certeza que deseja remover {self.usuario.get('nome', 'N/A')}?",
            QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            QMessageBox.information(self, "Removido", f"Usuário removido: {self.usuario.get('nome', 'N/A')}")
    
    def _mostrar_detalhes(self):
        """Mostra detalhes do usuário em um diálogo simples."""
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Detalhes - {self.usuario.get('nome', 'Usuário')}")
        dlg.setFixedWidth(300)
        
        layout = QVBoxLayout(dlg)
        layout.setSpacing(15)
        
        # Informações
        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(10)
        info_grid.setVerticalSpacing(8)
        
        campos = [
            ("Nome:", self.usuario.get('nome', 'N/A')),
            ("Email:", self.usuario.get('email', 'N/A')),
            ("Username:", self.usuario.get('username', 'N/A')),
            ("Perfil:", self._traduzir_cargo(self.usuario.get('perfil', 'user'))),
            ("Status:", "Ativo" if self.usuario.get('ativo', 1) == 1 else "Inativo"),
            ("Cadastro:", self._formatar_data(self.usuario.get('criado_em', 'N/A'))),
        ]
        
        for i, (label, valor) in enumerate(campos):
            label_widget = QLabel(f"<b>{label}</b>")
            label_widget.setStyleSheet(f"color: {TEXT_PRIMARY};")
            valor_widget = QLabel(str(valor))
            valor_widget.setStyleSheet(f"color: {TEXT_SECONDARY};")
            
            info_grid.addWidget(label_widget, i, 0)
            info_grid.addWidget(valor_widget, i, 1)
        
        layout.addLayout(info_grid)
        
        # Botão Fechar
        fechar_btn = QPushButton("Fechar")
        fechar_btn.setCursor(Qt.PointingHandCursor)
        fechar_btn.clicked.connect(dlg.accept)
        fechar_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px;
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_LIGHT};
            }}
        """)
        layout.addWidget(fechar_btn)
        
        dlg.exec_()
    
    def _formatar_data(self, data_str):
        """Formata a data para exibição."""
        if data_str == 'N/A':
            return data_str
        
        try:
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(data_str, fmt)
                    return dt.strftime("%d/%m/%Y")
                except:
                    continue
        except:
            pass
        
        return data_str


class UsuariosView(QWidget):
    """Lista simplificada de usuários."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = self._get_db_path()
        self.usuarios = []
        self._setup_ui()
        self.carregar_usuarios()

    def _get_db_path(self):
        """Obtém o caminho do banco de dados."""
        try:
            from src.config.paths import DB_DIR
            from database.db import get_db_path
            db_path = get_db_path(DB_DIR)
            if db_path.exists():
                return str(db_path)
        except Exception:
            pass

        possible_paths = [
            Path(__file__).parents[4] / 'database' / 'kamba_farma.db',
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
        """Configura a interface do usuário simplificada."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Cabeçalho simples
        header = self._criar_cabecalho()
        main_layout.addWidget(header)

        # Barra de controles
        controls = self._criar_controles()
        main_layout.addWidget(controls)

        # Área de scroll para os cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(scroll_area, 1)

        # Aplicar estilos
        self._aplicar_estilo()

    def _criar_cabecalho(self):
        """Cria o cabeçalho simplificado."""
        widget = QWidget()
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        titulo = QLabel("Usuários")
        titulo.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        """)
        
        descricao = QLabel("Gerencie os usuários do sistema")
        descricao.setStyleSheet(f"""
            font-size: 14px;
            color: {TEXT_SECONDARY};
        """)
        
        layout.addWidget(titulo)
        layout.addWidget(descricao)
        
        return widget

    def _criar_controles(self):
        """Cria a barra de controles."""
        widget = QWidget()
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Busca
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Buscar usuários...")
        self.input_search.setMinimumHeight(36)
        self.input_search.setMinimumWidth(250)
        self.input_search.textChanged.connect(self._on_search)
        
        # Filtro status
        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Ativos", "Inativos"])
        self.filtro_status.setMinimumHeight(36)
        self.filtro_status.setMinimumWidth(100)
        self.filtro_status.currentIndexChanged.connect(self._filtrar_usuarios)
        
        # Filtro cargo
        self.filtro_cargo = QComboBox()
        self.filtro_cargo.addItems(["Todos os cargos", "Administrador", "Farmacêutico", "Caixa", "Usuário"])
        self.filtro_cargo.setMinimumHeight(36)
        self.filtro_cargo.setMinimumWidth(140)
        self.filtro_cargo.currentIndexChanged.connect(self._filtrar_usuarios)
        
        layout.addWidget(self.input_search)
        layout.addWidget(self.filtro_status)
        layout.addWidget(self.filtro_cargo)
        layout.addStretch()
        
        # Botão adicionar
        add_btn = QPushButton("+ Adicionar Usuário")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._on_add)
        add_btn.setMinimumHeight(36)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 20px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_LIGHT};
            }}
        """)
        
        layout.addWidget(add_btn)
        
        return widget

    def _aplicar_estilo(self):
        """Aplica o estilo simplificado."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BACKGROUND};
                color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QLineEdit, QComboBox {{
                background-color: white;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 14px;
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border-color: {PRIMARY};
            }}
            
            QLineEdit::placeholder {{
                color: {TEXT_SECONDARY};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: white;
                color: {TEXT_PRIMARY};
                selection-background-color: {PRIMARY};
                border: 1px solid {BORDER};
            }}
            
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                background-color: #F5F5F5;
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: #9E9E9E;
            }}
        """)

    def carregar_usuarios(self):
        """Carrega os usuários do banco de dados."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(usuarios)")
            colunas = [row['name'] for row in cursor.fetchall()]
            
            campos = ['id', 'nome', 'email', 'username', 'perfil', 'ativo', 'criado_em']
            campos_disponiveis = [c for c in campos if c in colunas]
            
            if not campos_disponiveis:
                campos_disponiveis = ['id', 'nome']
                
            query = f"SELECT {', '.join(campos_disponiveis)} FROM usuarios ORDER BY id DESC"
            cursor.execute(query)
            
            self.usuarios = []
            for row in cursor.fetchall():
                usuario = dict(row)
                usuario['email'] = usuario.get('email', '')
                usuario['username'] = usuario.get('username', f"user{usuario['id']}")
                usuario['perfil'] = usuario.get('perfil', 'user')
                usuario['ativo'] = usuario.get('ativo', 1)
                usuario['criado_em'] = usuario.get('criado_em', 'N/A')
                self.usuarios.append(usuario)
            
            conn.close()
            self.atualizar_cards()
            
        except sqlite3.Error as e:
            self._mostrar_erro("Erro ao conectar ao banco de dados", str(e))
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
        for i in reversed(range(self.cards_layout.count())): 
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        for usuario in self.usuarios:
            card = UsuarioCard(usuario)
            self.cards_layout.addWidget(card)
        
        # Adicionar stretch no final
        self.cards_layout.addStretch()

    def _on_search(self):
        """Realiza busca nos usuários."""
        self._filtrar_usuarios()

    def _filtrar_usuarios(self):
        """Filtra os usuários com base nos critérios."""
        termo = self.input_search.text().lower()
        filtro_status = self.filtro_status.currentText()
        filtro_cargo = self.filtro_cargo.currentText()
        
        for i in reversed(range(self.cards_layout.count())): 
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
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
            if filtro_status == "Ativos" and usuario.get('ativo') != 1:
                continue
            elif filtro_status == "Inativos" and usuario.get('ativo') != 0:
                continue
            
            # Filtro por cargo
            if filtro_cargo != "Todos os cargos":
                cargo_esperado = filtro_cargo.split()[-1].lower()
                perfil = usuario.get('perfil', 'user')
                
                mapeamento = {
                    'administrador': 'admin',
                    'farmacêutico': 'farmaceutico',
                    'caixa': 'caixa',
                    'usuário': 'user'
                }
                
                if cargo_esperado in mapeamento and perfil != mapeamento[cargo_esperado]:
                    continue
            
            usuarios_filtrados.append(usuario)
        
        for usuario in usuarios_filtrados:
            card = UsuarioCard(usuario)
            self.cards_layout.addWidget(card)
        
        # Adicionar stretch no final
        self.cards_layout.addStretch()

    def _on_add(self):
        """Adiciona um novo usuário."""
        QMessageBox.information(self, "Adicionar", "Abrir formulário de adicionar usuário")

    def _mostrar_erro(self, titulo, mensagem):
        """Exibe uma mensagem de erro estilizada."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensagem)
        msg.exec_()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = UsuariosView()
    window.setWindowTitle("Usuários - Kamba Farma")
    window.resize(900, 600)
    window.show()
    
    sys.exit(app.exec_())