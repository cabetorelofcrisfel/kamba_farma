"""View que lista usuários registrados com tema claro moderno.

Exporta `UsuariosRegistradosView`, um QWidget que mostra uma
lista completa de usuários registrados no sistema com filtros e ações.
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QFrame, QComboBox, QLineEdit, QDateEdit,
    QHeaderView, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QBrush, QColor

# Paleta de cores - TEMA CLARO MODERNO
MILK_BG = "#FFFBF5"  # Cor de leite
CARD_BG = "#FFFFFF"  # Branco puro para cards
LIGHT_BORDER = "#E8E8E8"  # Borda cinza claro
ACCENT_BORDER = "#00BFA5"  # Borda de destaque teal
TEXT_PRIMARY = "#2C3E50"  # Azul escuro para texto principal
TEXT_SECONDARY = "#7F8C8D"  # Cinza para texto secundário
TEXT_LIGHT = "#95A5A6"  # Cinza mais claro
TEAL_PRIMARY = "#00BFA5"  # Teal principal
TEAL_LIGHT = "#E0F7FA"  # Teal muito claro para fundo
TEAL_HOVER = "#B2EBF2"  # Teal para hover
GREEN_SUCCESS = "#2ECC71"  # Verde mais moderno
RED_ERROR = "#E74C3C"  # Vermelho mais moderno
PURPLE = "#9B59B6"  # Roxo moderno
BLUE_INFO = "#3498DB"  # Azul moderno
ORANGE_ALERT = "#F39C12"  # Laranja moderno

class UsuariosRegistradosView(QWidget):
    """Lista completa de usuários registrados no sistema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = self._get_db_path()
        self.usuarios = []
        self._setup_ui()
        self.carregar_usuarios()
        self._apply_modern_styles()

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

        # Fallback: tenta encontrar o DB relativo à raiz do projeto
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

        placeholder_path = Path(__file__).parent / 'usuarios_demo.db'
        return str(placeholder_path)

    def _setup_ui(self):
        """Configura a interface do usuário."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)
        
        # Definir fundo leitoso
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(MILK_BG))
        self.setPalette(palette)

        # Cabeçalho melhorado
        header_widget = self._criar_cabecalho_melhorado()
        main_layout.addWidget(header_widget)

        # Estatísticas em cards modernos
        stats_widget = self._criar_estatisticas_melhoradas()
        main_layout.addWidget(stats_widget)

        # Filtros em card moderno
        filtros_widget = self._criar_filtros_melhorados()
        main_layout.addWidget(filtros_widget)

        # Tabela de usuários em card
        table_card = QFrame()
        table_card.setObjectName("tableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título da tabela
        table_header = QHBoxLayout()
        table_header.setContentsMargins(15, 15, 15, 10)
        
        table_title = QLabel("📋 Lista de Usuários")
        table_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
        """)
        
        table_header.addWidget(table_title)
        table_header.addStretch()
        table_layout.addLayout(table_header)
        
        self.tabela = self._criar_tabela_melhorada()
        table_layout.addWidget(self.tabela, 1)
        main_layout.addWidget(table_card, 1)

        # Barra de status melhorada
        status_widget = self._criar_barra_status_melhorada()
        main_layout.addWidget(status_widget)

    def _apply_modern_styles(self):
        """Aplica estilos modernos à interface."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {MILK_BG};
                color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            
            #headerCard {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {LIGHT_BORDER};
            }}
            
            #statsContainer {{
                background-color: transparent;
            }}
            
            #filterCard {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {LIGHT_BORDER};
                padding: 5px;
            }}
            
            #tableCard {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {LIGHT_BORDER};
            }}
            
            #statusCard {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {LIGHT_BORDER};
            }}
            
            .statCard {{
                background-color: {CARD_BG};
                border-radius: 10px;
                border: 1px solid {LIGHT_BORDER};
                padding: 5px;
            }}
            
            .statCard:hover {{
                border-color: {TEAL_PRIMARY};
                transform: translateY(-2px);
            }}
            
            QLineEdit, QComboBox, QDateEdit {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                border: 1px solid {LIGHT_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                selection-background-color: {TEAL_LIGHT};
                selection-color: {TEXT_PRIMARY};
            }}
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border-color: {TEAL_PRIMARY};
                border-width: 2px;
            }}
            
            QPushButton {{
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
                transition: all 0.2s ease;
            }}
            
            QPushButton:hover {{
                transform: translateY(-1px);
            }}
        """)

    def _criar_cabecalho_melhorado(self):
        """Cria o cabeçalho moderno da página."""
        widget = QFrame()
        widget.setObjectName("headerCard")
        widget.setMaximumHeight(100)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(25, 20, 25, 20)

        # Título com ícone
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        titulo = QLabel("👥 Gestão de Usuários")
        titulo.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
        """)

        subtitulo = QLabel("Gerencie e visualize todos os usuários cadastrados no sistema")
        subtitulo.setStyleSheet(f"""
            font-size: 13px;
            color: {TEXT_SECONDARY};
        """)

        title_layout.addWidget(titulo)
        title_layout.addWidget(subtitulo)

        layout.addWidget(title_widget)
        layout.addStretch()

        return widget

    def _criar_estatisticas_melhoradas(self):
        """Cria os cards de estatística modernos."""
        widget = QWidget()
        widget.setObjectName("statsContainer")
        widget.setMaximumHeight(110)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        stats_data = [
            ("👥", "Total", "0", TEAL_PRIMARY),
            ("✅", "Ativos", "0", GREEN_SUCCESS),
            ("⏸️", "Inativos", "0", RED_ERROR),
            ("👑", "Admins", "0", PURPLE),
            ("📅", "Hoje", "0", BLUE_INFO),
        ]

        for icon, nome, valor, cor in stats_data:
            stat_card = self._criar_stat_card_melhorado(icon, nome, valor, cor)
            layout.addWidget(stat_card)

        layout.addStretch()
        return widget

    def _criar_stat_card_melhorado(self, icon, nome, valor, cor):
        """Cria um card de estatística moderno."""
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedSize(140, 90)
        card.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

        # Linha superior: ícone e nome
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 18px;
            color: {cor};
        """)
        
        name_label = QLabel(nome)
        name_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {TEXT_SECONDARY};
        """)
        
        top_row.addWidget(icon_label)
        top_row.addStretch()
        top_row.addWidget(name_label)

        # Valor
        value_label = QLabel(valor)
        value_label.setObjectName(f"valor_{nome}")
        value_label.setStyleSheet(f"""
            font-size: 26px;
            font-weight: bold;
            color: {cor};
            qproperty-alignment: AlignRight;
        """)

        layout.addLayout(top_row)
        layout.addWidget(value_label)

        return card

    def _criar_filtros_melhorados(self):
        """Cria a barra de filtros moderna."""
        widget = QFrame()
        widget.setObjectName("filterCard")
        widget.setMaximumHeight(80)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Grupo de busca
        search_group = QWidget()
        search_layout = QHBoxLayout(search_group)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px;")
        
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar usuários...")
        self.busca_input.setFixedWidth(220)
        self.busca_input.textChanged.connect(self.filtrar_tabela)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.busca_input)

        # Grupo de status
        status_group = QWidget()
        status_layout = QHBoxLayout(status_group)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)

        status_label = QLabel("Status:")
        status_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {TEXT_SECONDARY};
        """)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Ativo", "Inativo"])
        self.filtro_status.setFixedWidth(120)
        self.filtro_status.currentIndexChanged.connect(self.filtrar_tabela)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.filtro_status)

        # Grupo de data
        date_group = QWidget()
        date_layout = QHBoxLayout(date_group)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(10)

        date_label = QLabel("Período:")
        date_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {TEXT_SECONDARY};
        """)

        hoje = QDate.currentDate()
        self.data_inicio = QDateEdit()
        self.data_inicio.setDate(hoje.addDays(-30))
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setFixedWidth(110)
        self.data_inicio.dateChanged.connect(self.filtrar_tabela)

        self.data_fim = QDateEdit()
        self.data_fim.setDate(hoje)
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setFixedWidth(110)
        self.data_fim.dateChanged.connect(self.filtrar_tabela)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.data_inicio)
        date_layout.addWidget(QLabel("até"))
        date_layout.addWidget(self.data_fim)

        layout.addWidget(search_group)
        layout.addWidget(status_group)
        layout.addWidget(date_group)
        layout.addStretch()

        # Botão de reset com estilo moderno
        btn_reset = QPushButton("🔄 Limpar Filtros")
        btn_reset.setFixedSize(140, 36)
        btn_reset.clicked.connect(self.resetar_filtros)
        btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: {TEXT_LIGHT}20;
                color: {TEXT_SECONDARY};
                border: 1px solid {LIGHT_BORDER};
            }}
            QPushButton:hover {{
                background-color: {TEXT_LIGHT}30;
                border-color: {TEXT_SECONDARY};
            }}
        """)
        layout.addWidget(btn_reset)

        return widget

    def _criar_tabela_melhorada(self):
        """Cria a tabela de usuários moderna."""
        tabela = QTableWidget()
        tabela.setObjectName("tabelaUsuarios")
        tabela.setColumnCount(9)
        tabela.setHorizontalHeaderLabels([
            "ID", "NOME", "Nº BILHETE", "ÁREA", "CONTACTO", "GÉNERO", "PERFIL", "STATUS", "CADASTRO"
        ])
        
        # Configurar estilo da tabela
        tabela.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD_BG};
                border: none;
                border-radius: 8px;
                gridline-color: {LIGHT_BORDER};
                font-size: 13px;
                selection-background-color: {TEAL_LIGHT};
                selection-color: {TEXT_PRIMARY};
            }}
            
            QTableWidget::item {{
                padding: 12px 8px;
                border-bottom: 1px solid {LIGHT_BORDER};
                color: {TEXT_PRIMARY};
            }}
            
            QTableWidget::item:selected {{
                background-color: {TEAL_LIGHT};
                color: {TEXT_PRIMARY};
            }}
            
            QHeaderView::section {{
                background-color: {MILK_BG};
                color: {TEXT_PRIMARY};
                padding: 14px 8px;
                border: none;
                border-bottom: 2px solid {TEAL_PRIMARY};
                font-weight: 600;
                font-size: 12.5px;
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
        
        # Configurar largura das colunas
        header = tabela.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nome
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Nº BI
        tabela.setColumnWidth(0, 70)   # ID
        tabela.setColumnWidth(3, 150)  # Área
        tabela.setColumnWidth(4, 130)  # Contacto
        tabela.setColumnWidth(5, 100)  # Género
        tabela.setColumnWidth(6, 140)  # Perfil
        tabela.setColumnWidth(7, 100)  # Status
        tabela.setColumnWidth(8, 150)  # Cadastro
        
        tabela.verticalHeader().setVisible(False)
        tabela.setAlternatingRowColors(True)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setSelectionMode(QTableWidget.SingleSelection)
        tabela.setShowGrid(False)
        
        # Conectar sinal de clique
        tabela.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        return tabela

    def _criar_barra_status_melhorada(self):
        """Cria a barra de status moderna."""
        widget = QFrame()
        widget.setObjectName("statusCard")
        widget.setMaximumHeight(70)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(25, 15, 25, 15)

        # Contador
        self.contador_label = QLabel("Carregando registros...")
        self.contador_label.setStyleSheet(f"""
            font-size: 14px;
            color: {TEXT_SECONDARY};
            font-weight: 600;
        """)

        layout.addWidget(self.contador_label)
        layout.addStretch()

        # Botões de ação com estilo moderno
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(10)

        acoes = [
            ("🔄", "Atualizar", self.atualizar_lista, TEAL_PRIMARY),
            ("📤", "Exportar", self.exportar_csv, BLUE_INFO),
            ("🖨️", "Imprimir", self.imprimir_lista, PURPLE),
            ("📋", "Copiar", self.copiar_lista, ORANGE_ALERT),
        ]

        for icon, texto, funcao, cor in acoes:
            btn = QPushButton(f"{icon} {texto}")
            btn.setFixedHeight(38)
            btn.setMinimumWidth(120)
            btn.clicked.connect(funcao)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {cor}DD;
                }}
                QPushButton:pressed {{
                    background-color: {cor}AA;
                }}
            """)
            acoes_layout.addWidget(btn)

        layout.addLayout(acoes_layout)
        return widget

    def carregar_usuarios(self):
        """Carrega os usuários do banco de dados."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Verificar estrutura da tabela
            cursor.execute("PRAGMA table_info(usuarios)")
            colunas = [row['name'] for row in cursor.fetchall()]
            
            # Construir query com colunas relevantes disponíveis
            wanted = ['id','nome','numero_bi','area_atuacao','contacto','genero','perfil','ativo','criado_em']
            campos_disponiveis = [c for c in wanted if c in colunas]
            if not campos_disponiveis:
                campos_disponiveis = ['id','nome']
            query = f"SELECT {', '.join(campos_disponiveis)} FROM usuarios ORDER BY id DESC"
            cursor.execute(query)
            
            self.usuarios = []
            for row in cursor.fetchall():
                usuario = dict(row)
                usuario['perfil'] = usuario.get('perfil', 'user')
                usuario['ativo'] = usuario.get('ativo', 1)
                usuario['criado_em'] = usuario.get('criado_em', 'N/A')
                self.usuarios.append(usuario)
            
            conn.close()
            self.atualizar_tabela()
            self.atualizar_estatisticas_melhoradas()

        except sqlite3.Error as e:
            self._mostrar_erro_melhorado("Erro ao conectar ao banco de dados", str(e))
            self.usuarios = []
            self.atualizar_tabela()

    def atualizar_tabela(self):
        """Atualiza a tabela com os dados dos usuários."""
        self.tabela.setRowCount(0)
        for i, usuario in enumerate(self.usuarios):
            self.tabela.insertRow(i)

            # ID
            item_id = QTableWidgetItem(str(usuario.get('id', '')))
            item_id.setTextAlignment(Qt.AlignCenter)
            item_id.setForeground(QBrush(QColor(TEXT_SECONDARY)))
            self.tabela.setItem(i, 0, item_id)

            # Nome
            nome = usuario.get('nome', 'N/A')
            item_nome = QTableWidgetItem(nome)
            item_nome.setForeground(QBrush(QColor(TEXT_PRIMARY)))
            self.tabela.setItem(i, 1, item_nome)

            # Número BI
            numero_bi = usuario.get('numero_bi', '')
            item_bi = QTableWidgetItem(numero_bi or '')
            item_bi.setForeground(QBrush(QColor(TEXT_SECONDARY)))
            self.tabela.setItem(i, 2, item_bi)

            # Área de atuação
            area = usuario.get('area_atuacao', '')
            item_area = QTableWidgetItem(area or '')
            self.tabela.setItem(i, 3, item_area)

            # Contacto
            contacto = usuario.get('contacto', '')
            item_contacto = QTableWidgetItem(contacto or '')
            item_contacto.setForeground(QBrush(QColor(TEAL_PRIMARY)))
            self.tabela.setItem(i, 4, item_contacto)

            # Género
            genero = usuario.get('genero', '')
            item_genero = QTableWidgetItem(genero or '')
            self.tabela.setItem(i, 5, item_genero)

            # Perfil
            perfil = usuario.get('perfil', 'user')
            item_perfil = QTableWidgetItem(self._traduzir_cargo(perfil))
            item_perfil.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 6, item_perfil)

            # Status
            ativo = usuario.get('ativo', 0)
            if ativo == 1:
                status = "✅ Ativo"
                item_status = QTableWidgetItem(status)
                item_status.setForeground(QBrush(QColor(GREEN_SUCCESS)))
            else:
                status = "⏸️ Inativo"
                item_status = QTableWidgetItem(status)
                item_status.setForeground(QBrush(QColor(RED_ERROR)))
            item_status.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 7, item_status)

            # Data de cadastro
            criado_em = usuario.get('criado_em', 'N/A')
            item_cadastro = QTableWidgetItem(criado_em)
            item_cadastro.setTextAlignment(Qt.AlignCenter)
            item_cadastro.setForeground(QBrush(QColor(TEXT_SECONDARY)))
            self.tabela.setItem(i, 8, item_cadastro)
        
        self.atualizar_contador_melhorado()

    def atualizar_estatisticas_melhoradas(self):
        """Atualiza os cards de estatística modernos."""
        total = len(self.usuarios)
        ativos = sum(1 for u in self.usuarios if u.get('ativo') == 1)
        inativos = total - ativos
        admins = sum(1 for u in self.usuarios if u.get('perfil') == 'admin')
        
        hoje = datetime.now().date()
        hoje_str = hoje.strftime("%Y-%m-%d")
        hoje_cadastros = sum(1 for u in self.usuarios 
                           if str(u.get('criado_em', '')).startswith(hoje_str))
        
        # Encontrar e atualizar os labels
        for widget in self.findChildren(QFrame):
            if widget.objectName() == "statCard":
                valor_label = widget.findChild(QLabel)
                if valor_label and valor_label.objectName().startswith("valor_"):
                    nome = valor_label.objectName()[6:]
                    if nome == "Total":
                        valor_label.setText(str(total))
                    elif nome == "Ativos":
                        valor_label.setText(str(ativos))
                    elif nome == "Inativos":
                        valor_label.setText(str(inativos))
                    elif nome == "Admins":
                        valor_label.setText(str(admins))
                    elif nome == "Hoje":
                        valor_label.setText(str(hoje_cadastros))

    def atualizar_contador_melhorado(self):
        """Atualiza o contador de registros."""
        total = self.tabela.rowCount()
        visible = sum(1 for i in range(total) if not self.tabela.isRowHidden(i))
        self.contador_label.setText(f"📊 Mostrando {visible} de {total} usuário(s)")

    def _traduzir_cargo(self, perfil):
        """Traduz o código do perfil para um nome amigável."""
        traducoes = {
            'admin': '👑 Administrador',
            'farmaceutico': '💊 Farmacêutico',
            'caixa': '💰 Caixa',
            'gerente': '👔 Gerente',
            'user': '👤 Usuário'
        }
        return traducoes.get(perfil, perfil.capitalize())

    def filtrar_tabela(self):
        """Filtra a tabela com base nos critérios selecionados."""
        termo_busca = self.busca_input.text().lower()
        status_filtro = self.filtro_status.currentText()
        data_inicio = self.data_inicio.date()
        data_fim = self.data_fim.date()
        
        for i in range(self.tabela.rowCount()):
            mostrar = True
            
            # Filtro por busca
            if termo_busca:
                nome = self.tabela.item(i, 1).text().lower()
                bi = self.tabela.item(i, 2).text().lower()
                contacto = self.tabela.item(i, 4).text().lower()
                
                if not (termo_busca in nome or termo_busca in bi or termo_busca in contacto):
                    mostrar = False
            
            # Filtro por status
            if status_filtro != "Todos" and mostrar:
                status_item = self.tabela.item(i, 7)
                status_text = "Ativo" if "✅" in status_item.text() else "Inativo"
                if status_filtro != status_text:
                    mostrar = False
            
            # Filtro por data
            if mostrar:
                try:
                    data_cadastro_str = self.tabela.item(i, 8).text()
                    if data_cadastro_str != "N/A":
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
                            try:
                                data_cadastro = datetime.strptime(data_cadastro_str.split()[0], fmt).date()
                                data_cadastro_qdate = QDate(data_cadastro.year, data_cadastro.month, data_cadastro.day)
                                if data_cadastro_qdate < data_inicio or data_cadastro_qdate > data_fim:
                                    mostrar = False
                                break
                            except ValueError:
                                continue
                except:
                    pass
            
            self.tabela.setRowHidden(i, not mostrar)
        
        self.atualizar_contador_melhorado()

    def resetar_filtros(self):
        """Reseta todos os filtros."""
        self.busca_input.clear()
        self.filtro_status.setCurrentIndex(0)
        
        hoje = QDate.currentDate()
        self.data_inicio.setDate(hoje.addDays(-30))
        self.data_fim.setDate(hoje)
        
        for i in range(self.tabela.rowCount()):
            self.tabela.setRowHidden(i, False)
        
        self.atualizar_contador_melhorado()

    def atualizar_lista(self):
        """Atualiza a lista de usuários."""
        self.carregar_usuarios()
        self._mostrar_notificacao("Lista de usuários atualizada com sucesso!", "success")

    def exportar_csv(self):
        """Exporta a lista de usuários para CSV."""
        from PyQt5.QtWidgets import QFileDialog
        
        arquivo, _ = QFileDialog.getSaveFileName(
            self, "Exportar para CSV", "usuarios_kamba_farma.csv", "CSV Files (*.csv)"
        )
        
        if arquivo:
            try:
                import csv
                with open(arquivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    
                    headers = [self.tabela.horizontalHeaderItem(i).text() 
                              for i in range(self.tabela.columnCount())]
                    writer.writerow(headers)
                    
                    for i in range(self.tabela.rowCount()):
                        if not self.tabela.isRowHidden(i):
                            row = []
                            for j in range(self.tabela.columnCount()):
                                item = self.tabela.item(i, j)
                                row.append(item.text() if item else "")
                            writer.writerow(row)
                
                self._mostrar_notificacao(f"Arquivo exportado com sucesso!\n{arquivo}", "success")
                    
            except Exception as e:
                self._mostrar_erro_melhorado("Erro ao exportar CSV", str(e))

    def imprimir_lista(self):
        """Prepara a impressão da lista."""
        self._mostrar_notificacao("Função de impressão em desenvolvimento...", "info")

    def copiar_lista(self):
        """Copia a lista selecionada para a área de transferência."""
        import pyperclip
        
        texto = ""
        headers = [self.tabela.horizontalHeaderItem(i).text() 
                  for i in range(self.tabela.columnCount())]
        texto += "\t".join(headers) + "\n"
        
        for i in range(self.tabela.rowCount()):
            if not self.tabela.isRowHidden(i):
                row = []
                for j in range(self.tabela.columnCount()):
                    item = self.tabela.item(i, j)
                    row.append(item.text() if item else "")
                texto += "\t".join(row) + "\n"
        
        pyperclip.copy(texto)
        self._mostrar_notificacao("Lista copiada para a área de transferência!", "success")

    def _on_item_double_clicked(self, item):
        """Abre detalhes do usuário ao clicar duas vezes."""
        row = item.row()
        usuario_id = self.tabela.item(row, 0).text()
        usuario_nome = self.tabela.item(row, 1).text()
        detalhes = f"""
        <h3 style='color:{TEAL_PRIMARY};'>👤 Detalhes do Usuário</h3>
        <p><b>ID:</b> {usuario_id}</p>
        <p><b>Nome:</b> {usuario_nome}</p>
        <p><b>Nº Bilhete:</b> {self.tabela.item(row, 2).text()}</p>
        <p><b>Área de Atuação:</b> {self.tabela.item(row, 3).text()}</p>
        <p><b>Contacto:</b> {self.tabela.item(row, 4).text()}</p>
        <p><b>Género:</b> {self.tabela.item(row, 5).text()}</p>
        <p><b>Perfil:</b> {self.tabela.item(row, 6).text()}</p>
        <p><b>Status:</b> {self.tabela.item(row, 7).text()}</p>
        <p><b>Cadastrado em:</b> {self.tabela.item(row, 8).text()}</p>
        """
        
        msg = QMessageBox()
        msg.setWindowTitle("Detalhes do Usuário")
        msg.setText(detalhes)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {CARD_BG};
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 13px;
                line-height: 1.6;
            }}
        """)
        msg.exec_()

    def _mostrar_notificacao(self, mensagem, tipo="info"):
        """Exibe uma notificação moderna."""
        from PyQt5.QtWidgets import QLabel
        from PyQt5.QtCore import QTimer, QPropertyAnimation
        
        notificacao = QLabel(mensagem, self)
        
        cores = {
            "success": GREEN_SUCCESS,
            "error": RED_ERROR,
            "warning": ORANGE_ALERT,
            "info": TEAL_PRIMARY
        }
        
        cor = cores.get(tipo, TEAL_PRIMARY)
        
        notificacao.setStyleSheet(f"""
            QLabel {{
                background-color: {cor};
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
            }}
        """)
        
        notificacao.adjustSize()
        notificacao.move(self.width() - notificacao.width() - 30, 30)
        notificacao.show()
        
        QTimer.singleShot(3000, notificacao.deleteLater)

    def _mostrar_erro_melhorado(self, titulo, mensagem):
        """Exibe uma mensagem de erro estilizada modernamente."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(titulo)
        msg.setText(mensagem)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {CARD_BG};
                color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                border-radius: 12px;
            }}
            QMessageBox QLabel {{
                color: {TEXT_PRIMARY};
            }}
            QMessageBox QPushButton {{
                background-color: {TEAL_PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {TEAL_PRIMARY}DD;
            }}
        """)
        msg.exec_()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Estilo global moderno
    app.setStyleSheet(f"""
        QApplication {{
            background-color: {MILK_BG};
        }}
    """)
    
    window = UsuariosRegistradosView()
    window.setWindowTitle("Gestão de Usuários - Kamba Farma")
    window.resize(1400, 850)
    window.show()
    
    sys.exit(app.exec_())