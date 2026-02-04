"""View simplificada de usuários registrados.

Exporta `UsuariosRegistradosView`, um QWidget que mostra uma
lista de usuários com filtros básicos e ações essenciais.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QFrame, QComboBox, QLineEdit,
    QHeaderView, QSizePolicy, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

from colors import *
# Cores simplificadas
BACKGROUND = WHITE
TABLE_BG = WHITE
BORDER = "#E0E0E0"
TEXT_PRIMARY = TEXT_PRIMARY
TEXT_SECONDARY = "#757575"
PRIMARY = PRIMARY_COLOR
PRIMARY_LIGHT = "#80CBC4"
GREEN = "#4CAF50"
RED = ACCENT_RED
BLUE = "#2196F3"


class UsuariosRegistradosView(QWidget):
    """Lista simplificada de usuários registrados no sistema."""

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
        """Configura a interface simplificada."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Cabeçalho simples
        header = self._criar_cabecalho_simples()
        main_layout.addWidget(header)

        # Barra de controles
        controls = self._criar_controles_simples()
        main_layout.addWidget(controls)

        # Tabela
        self.tabela = self._criar_tabela_simples()
        main_layout.addWidget(self.tabela, 1)

        # Barra de ações
        actions = self._criar_barra_acoes_simples()
        main_layout.addWidget(actions)

        # Aplicar estilos
        self._aplicar_estilo_simples()

    def _criar_cabecalho_simples(self):
        """Cria cabeçalho simplificado."""
        widget = QWidget()
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        titulo = QLabel("Usuários Registrados")
        titulo.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        """)
        
        descricao = QLabel("Lista completa de usuários do sistema")
        descricao.setStyleSheet(f"""
            font-size: 13px;
            color: {TEXT_SECONDARY};
        """)
        
        layout.addWidget(titulo)
        layout.addWidget(descricao)
        
        return widget

    def _criar_controles_simples(self):
        """Cria controles de busca e filtro simplificados."""
        widget = QWidget()
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Busca
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar por nome, contacto ou BI...")
        self.busca_input.setMinimumHeight(36)
        self.busca_input.textChanged.connect(self.filtrar_tabela)
        
        # Filtro status
        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Ativos", "Inativos"])
        self.filtro_status.setMinimumHeight(36)
        self.filtro_status.setMinimumWidth(120)
        self.filtro_status.currentIndexChanged.connect(self.filtrar_tabela)
        
        # Filtro perfil
        self.filtro_perfil = QComboBox()
        self.filtro_perfil.addItems(["Todos os perfis", "Administrador", "Farmacêutico", "Caixa", "Usuário"])
        self.filtro_perfil.setMinimumHeight(36)
        self.filtro_perfil.setMinimumWidth(140)
        self.filtro_perfil.currentIndexChanged.connect(self.filtrar_tabela)
        
        layout.addWidget(self.busca_input, 2)
        layout.addWidget(self.filtro_status)
        layout.addWidget(self.filtro_perfil)
        layout.addStretch()
        
        # Botão limpar
        btn_limpar = QPushButton("Limpar Filtros")
        btn_limpar.setMinimumHeight(36)
        btn_limpar.setCursor(Qt.PointingHandCursor)
        btn_limpar.clicked.connect(self.limpar_filtros)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {TEXT_SECONDARY}20;
                color: {TEXT_SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 15px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {TEXT_SECONDARY}30;
            }}
        """)
        
        layout.addWidget(btn_limpar)
        
        return widget

    def _criar_tabela_simples(self):
        """Cria tabela simplificada."""
        tabela = QTableWidget()
        tabela.setColumnCount(7)
        tabela.setHorizontalHeaderLabels([
            "ID", "NOME", "CONTACTO", "PERFIL", "STATUS", "CADASTRO", "AÇÕES"
        ])
        
        # Configurar largura das colunas
        header = tabela.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nome
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Contacto
        tabela.setColumnWidth(0, 60)    # ID
        tabela.setColumnWidth(3, 120)   # Perfil
        tabela.setColumnWidth(4, 80)    # Status
        tabela.setColumnWidth(5, 120)   # Cadastro
        tabela.setColumnWidth(6, 80)    # Ações
        
        tabela.verticalHeader().setVisible(False)
        tabela.setAlternatingRowColors(True)
        tabela.setSelectionBehavior(QTableWidget.SelectRows)
        tabela.setSelectionMode(QTableWidget.SingleSelection)
        tabela.setShowGrid(False)
        
        # Conectar clique duplo
        tabela.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        return tabela

    def _criar_barra_acoes_simples(self):
        """Cria barra de ações simplificada."""
        widget = QWidget()
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Contador
        self.contador_label = QLabel("Carregando...")
        self.contador_label.setStyleSheet(f"""
            font-size: 13px;
            color: {TEXT_SECONDARY};
        """)
        
        layout.addWidget(self.contador_label)
        layout.addStretch()
        
        # Botões
        acoes = [
            ("Atualizar", self.atualizar_lista, BLUE),
            ("Exportar", self.exportar_csv, GREEN),
        ]
        
        for texto, funcao, cor in acoes:
            btn = QPushButton(texto)
            btn.setMinimumHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(funcao)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 0 20px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {cor}DD;
                }}
            """)
            layout.addWidget(btn)
        
        return widget

    def _aplicar_estilo_simples(self):
        """Aplica estilo simplificado."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BACKGROUND};
                color: {TEXT_PRIMARY};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QTableWidget {{
                background-color: {TABLE_BG};
                border: 1px solid {BORDER};
                border-radius: 6px;
                font-size: 13px;
                selection-background-color: {PRIMARY}20;
                selection-color: {TEXT_PRIMARY};
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {BORDER};
            }}
            
            QHeaderView::section {{
                background-color: {BACKGROUND};
                color: {TEXT_PRIMARY};
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid {PRIMARY};
                font-weight: 600;
                font-size: 12px;
            }}
            
            QLineEdit, QComboBox {{
                background-color: white;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 0 12px;
                font-size: 13px;
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border-color: {PRIMARY};
            }}
            
            QLineEdit::placeholder {{
                color: {TEXT_SECONDARY};
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
                background-color: {PRIMARY};
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
            
            # Selecionar colunas disponíveis
            wanted = ['id', 'nome', 'numero_bi', 'contacto', 'perfil', 'ativo', 'criado_em']
            campos_disponiveis = [c for c in wanted if c in colunas]
            if not campos_disponiveis:
                campos_disponiveis = ['id', 'nome']
            
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
            
        except sqlite3.Error as e:
            self._mostrar_erro("Erro ao conectar ao banco de dados", str(e))
            self.carregar_dados_demo()

    def carregar_dados_demo(self):
        """Carrega dados de demonstração."""
        self.usuarios = [
            {
                'id': 1, 'nome': 'Administrador Sistema', 'contacto': 'admin@kambafarma.com',
                'numero_bi': '123456789LA012', 'perfil': 'admin', 'ativo': 1,
                'criado_em': '2024-01-15 10:30:00'
            },
            {
                'id': 2, 'nome': 'Maria Silva', 'contacto': 'maria@kambafarma.com',
                'numero_bi': '987654321LA013', 'perfil': 'farmaceutico', 'ativo': 1,
                'criado_em': '2024-02-10 09:15:00'
            },
            {
                'id': 3, 'nome': 'João Santos', 'contacto': 'joao@kambafarma.com',
                'numero_bi': '456789123LA014', 'perfil': 'caixa', 'ativo': 1,
                'criado_em': '2024-02-28 14:00:00'
            },
            {
                'id': 4, 'nome': 'Ana Oliveira', 'contacto': 'ana@kambafarma.com',
                'numero_bi': '321654987LA015', 'perfil': 'gerente', 'ativo': 0,
                'criado_em': '2024-03-05 11:45:00'
            },
            {
                'id': 5, 'nome': 'Carlos Mendes', 'contacto': 'carlos@kambafarma.com',
                'numero_bi': '789123456LA016', 'perfil': 'user', 'ativo': 1,
                'criado_em': '2024-03-12 08:20:00'
            },
        ]
        self.atualizar_tabela()

    def atualizar_tabela(self):
        """Atualiza a tabela com os dados dos usuários."""
        self.tabela.setRowCount(0)
        for i, usuario in enumerate(self.usuarios):
            self.tabela.insertRow(i)

            # ID
            item_id = QTableWidgetItem(str(usuario.get('id', '')))
            item_id.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 0, item_id)

            # Nome
            nome = usuario.get('nome', 'N/A')
            item_nome = QTableWidgetItem(nome)
            self.tabela.setItem(i, 1, item_nome)

            # Contacto
            contacto = usuario.get('contacto', '')
            item_contacto = QTableWidgetItem(contacto)
            self.tabela.setItem(i, 2, item_contacto)

            # Perfil
            perfil = usuario.get('perfil', 'user')
            item_perfil = QTableWidgetItem(self._traduzir_cargo(perfil))
            item_perfil.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 3, item_perfil)

            # Status
            ativo = usuario.get('ativo', 0)
            if ativo == 1:
                status = "● Ativo"
                item_status = QTableWidgetItem(status)
                item_status.setForeground(QBrush(QColor(GREEN)))
            else:
                status = "○ Inativo"
                item_status = QTableWidgetItem(status)
                item_status.setForeground(QBrush(QColor(RED)))
            item_status.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 4, item_status)

            # Data de cadastro
            criado_em = usuario.get('criado_em', 'N/A')
            data_formatada = self._formatar_data(criado_em)
            item_cadastro = QTableWidgetItem(data_formatada)
            item_cadastro.setTextAlignment(Qt.AlignCenter)
            self.tabela.setItem(i, 5, item_cadastro)

            # Botão de ações
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(4)
            
            btn_ver = QPushButton("👁")
            btn_ver.setToolTip("Ver detalhes")
            btn_ver.setFixedSize(30, 30)
            btn_ver.setCursor(Qt.PointingHandCursor)
            btn_ver.clicked.connect(lambda checked, row=i: self.ver_detalhes(row))
            btn_ver.setStyleSheet(f"""
                QPushButton {{
                    background-color: {BLUE}20;
                    color: {BLUE};
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {BLUE}40;
                }}
            """)
            
            btn_editar = QPushButton("✏")
            btn_editar.setToolTip("Editar")
            btn_editar.setFixedSize(30, 30)
            btn_editar.setCursor(Qt.PointingHandCursor)
            btn_editar.clicked.connect(lambda checked, row=i: self.editar_usuario(row))
            btn_editar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PRIMARY}20;
                    color: {PRIMARY};
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {PRIMARY}40;
                }}
            """)
            
            btn_layout.addWidget(btn_ver)
            btn_layout.addWidget(btn_editar)
            btn_layout.addStretch()
            
            self.tabela.setCellWidget(i, 6, btn_widget)
        
        self.atualizar_contador()

    def _traduzir_cargo(self, perfil):
        """Traduz o código do perfil para um nome amigável."""
        traducoes = {
            'admin': 'Administrador',
            'farmaceutico': 'Farmacêutico',
            'caixa': 'Caixa',
            'gerente': 'Gerente',
            'user': 'Usuário'
        }
        return traducoes.get(perfil, perfil.capitalize())

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

    def atualizar_contador(self):
        """Atualiza o contador de registros."""
        total = self.tabela.rowCount()
        visible = sum(1 for i in range(total) if not self.tabela.isRowHidden(i))
        self.contador_label.setText(f"Mostrando {visible} de {total} usuário(s)")

    def filtrar_tabela(self):
        """Filtra a tabela com base nos critérios selecionados."""
        termo_busca = self.busca_input.text().lower()
        status_filtro = self.filtro_status.currentText()
        perfil_filtro = self.filtro_perfil.currentText()
        
        for i in range(self.tabela.rowCount()):
            mostrar = True
            
            # Filtro por busca
            if termo_busca:
                nome = self.tabela.item(i, 1).text().lower()
                contacto = self.tabela.item(i, 2).text().lower()
                
                if not (termo_busca in nome or termo_busca in contacto):
                    mostrar = False
            
            # Filtro por status
            if status_filtro != "Todos" and mostrar:
                status_item = self.tabela.item(i, 4)
                status_text = "Ativo" if "Ativo" in status_item.text() else "Inativo"
                if status_filtro != status_text:
                    mostrar = False
            
            # Filtro por perfil
            if perfil_filtro != "Todos os perfis" and mostrar:
                perfil_item = self.tabela.item(i, 3).text().strip()
                if perfil_filtro != perfil_item:
                    mostrar = False
            
            self.tabela.setRowHidden(i, not mostrar)
        
        self.atualizar_contador()

    def limpar_filtros(self):
        """Limpa todos os filtros."""
        self.busca_input.clear()
        self.filtro_status.setCurrentIndex(0)
        self.filtro_perfil.setCurrentIndex(0)
        
        for i in range(self.tabela.rowCount()):
            self.tabela.setRowHidden(i, False)
        
        self.atualizar_contador()

    def ver_detalhes(self, row):
        """Mostra detalhes do usuário."""
        usuario = self.usuarios[row]
        detalhes = f"""
        <h3>Detalhes do Usuário</h3>
        <p><b>ID:</b> {usuario.get('id', 'N/A')}</p>
        <p><b>Nome:</b> {usuario.get('nome', 'N/A')}</p>
        <p><b>Nº BI:</b> {usuario.get('numero_bi', 'N/A')}</p>
        <p><b>Contacto:</b> {usuario.get('contacto', 'N/A')}</p>
        <p><b>Perfil:</b> {self._traduzir_cargo(usuario.get('perfil', 'user'))}</p>
        <p><b>Status:</b> {'Ativo' if usuario.get('ativo') == 1 else 'Inativo'}</p>
        <p><b>Cadastrado em:</b> {self._formatar_data(usuario.get('criado_em', 'N/A'))}</p>
        """
        
        msg = QMessageBox()
        msg.setWindowTitle("Detalhes do Usuário")
        msg.setText(detalhes)
        msg.exec_()

    def editar_usuario(self, row):
        """Edita o usuário."""
        usuario = self.usuarios[row]
        QMessageBox.information(self, "Editar", f"Editar usuário: {usuario.get('nome', 'N/A')}")

    def atualizar_lista(self):
        """Atualiza a lista de usuários."""
        self.carregar_usuarios()
        QMessageBox.information(self, "Atualizar", "Lista de usuários atualizada!")

    def exportar_csv(self):
        """Exporta a lista para CSV."""
        from PyQt5.QtWidgets import QFileDialog
        
        arquivo, _ = QFileDialog.getSaveFileName(
            self, "Exportar para CSV", "usuarios.csv", "CSV Files (*.csv)"
        )
        
        if arquivo:
            try:
                import csv
                with open(arquivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    
                    # Cabeçalho
                    headers = [self.tabela.horizontalHeaderItem(i).text() 
                              for i in range(self.tabela.columnCount())]
                    writer.writerow(headers[:-1])  # Excluir coluna de ações
                    
                    # Dados
                    for i in range(self.tabela.rowCount()):
                        if not self.tabela.isRowHidden(i):
                            row_data = []
                            for j in range(self.tabela.columnCount() - 1):  # Excluir ações
                                if j == 6:  # Pular coluna de ações
                                    continue
                                item = self.tabela.item(i, j)
                                if item:
                                    # Remover símbolos de status
                                    text = item.text()
                                    if j == 4:  # Coluna de status
                                        text = text.replace("● ", "").replace("○ ", "")
                                    row_data.append(text)
                                else:
                                    row_data.append("")
                            writer.writerow(row_data)
                
                QMessageBox.information(self, "Exportar", f"Arquivo exportado: {arquivo}")
                    
            except Exception as e:
                self._mostrar_erro("Erro ao exportar", str(e))

    def _on_item_double_clicked(self, item):
        """Abre detalhes ao clicar duas vezes."""
        self.ver_detalhes(item.row())

    def _mostrar_erro(self, titulo, mensagem):
        """Exibe mensagem de erro."""
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
    
    window = UsuariosRegistradosView()
    window.setWindowTitle("Usuários Registrados")
    window.resize(1000, 600)
    window.show()
    
    sys.exit(app.exec_())