from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QDialog, QFormLayout, QComboBox, QSpinBox, QTextEdit, QTabWidget,
    QListWidget, QListWidgetItem, QSplitter, QHeaderView, QScrollArea
)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import os
import sys
from pathlib import Path

# Add src to path
src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_root not in sys.path:
    sys.path.insert(0, src_root)

from database.sql_manager import SQLDatabaseManager


class CreateTableDialog(QDialog):
    """Dialog para criar nova tabela"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Criar Nova Tabela')
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        self.table_name = None
        self.columns = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Table name
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        form_layout.addRow('Nome da Tabela:', self.name_input)
        layout.addLayout(form_layout)
        
        # Columns section
        col_label = QLabel('Colunas:')
        col_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        layout.addWidget(col_label)
        
        # Column inputs
        self.columns_list = QListWidget()
        layout.addWidget(self.columns_list)
        
        # Add column button
        col_button_layout = QHBoxLayout()
        
        self.col_name = QLineEdit()
        self.col_name.setPlaceholderText('Nome da coluna')
        col_button_layout.addWidget(self.col_name)
        
        self.col_type = QComboBox()
        self.col_type.addItems(['TEXT', 'INTEGER', 'REAL', 'BLOB', 'DATE', 'DATETIME'])
        col_button_layout.addWidget(self.col_type)
        
        self.col_pk = QComboBox()
        self.col_pk.addItems(['Padrão', 'PRIMARY KEY', 'NOT NULL', 'UNIQUE'])
        col_button_layout.addWidget(self.col_pk)
        
        add_col_btn = QPushButton('Adicionar Coluna')
        add_col_btn.clicked.connect(self.add_column)
        col_button_layout.addWidget(add_col_btn)
        
        layout.addLayout(col_button_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton('Criar Tabela')
        create_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton('Cancelar')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def add_column(self):
        """Adiciona coluna à lista"""
        col_name = self.col_name.text().strip()
        col_type = self.col_type.currentText()
        col_attr = self.col_pk.currentText()
        
        if not col_name:
            QMessageBox.warning(self, 'Aviso', 'Digite o nome da coluna')
            return
        
        # Criar definição completa
        col_def = f'{col_type}'
        if col_attr != 'Padrão':
            col_def += f' {col_attr}'
        
        self.columns[col_name] = col_def
        
        # Adicionar à lista
        item_text = f'{col_name} ({col_def})'
        self.columns_list.addItem(item_text)
        
        # Limpar inputs
        self.col_name.clear()
        self.col_type.setCurrentIndex(0)
        self.col_pk.setCurrentIndex(0)
    
    def get_table_info(self) -> tuple:
        """Retorna nome e colunas da tabela"""
        table_name = self.name_input.text().strip()
        
        if not table_name:
            raise ValueError('Nome da tabela é obrigatório')
        
        if not self.columns:
            raise ValueError('Adicione pelo menos uma coluna')
        
        # Se não houver ID, adicionar um
        if 'id' not in self.columns and not any('PRIMARY KEY' in v for v in self.columns.values()):
            columns_with_id = {'id': 'INTEGER PRIMARY KEY AUTOINCREMENT'}
            columns_with_id.update(self.columns)
            return table_name, columns_with_id
        
        return table_name, self.columns


class InsertDataDialog(QDialog):
    """Dialog para inserir dados"""
    
    def __init__(self, table_name: str, columns: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'Inserir Dados - {table_name}')
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        self.table_name = table_name
        self.columns = columns
        self.data = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.inputs = {}
        
        for col in self.columns:
            # Pular coluna ID se for autoincrementada
            if col['name'].lower() == 'id' and 'AUTOINCREMENT' in col['type']:
                continue
            
            label = QLabel(col['name'])
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"Digite o valor ({col['type']})")
            
            self.inputs[col['name']] = input_field
            form_layout.addRow(label, input_field)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        insert_btn = QPushButton('Inserir')
        insert_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton('Cancelar')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(insert_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_data(self) -> dict:
        """Retorna dados inseridos"""
        for col_name, input_field in self.inputs.items():
            self.data[col_name] = input_field.text().strip()
        return self.data


class SQLDatabaseGUI(QMainWindow):
    """Interface gráfica para gerenciador de banco de dados SQL"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gerenciador de Banco de Dados SQL')
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(1000, 600)
        
        self.db_manager = None
        self.current_table = None
        
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Configura a interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Database operations
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel('Gerenciador SQL')
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        left_layout.addWidget(title)
        
        # Database file selection
        db_layout = QHBoxLayout()
        self.db_path_label = QLineEdit()
        self.db_path_label.setReadOnly(True)
        self.db_path_label.setPlaceholderText('Banco de dados não carregado')
        db_layout.addWidget(self.db_path_label)
        
        open_db_btn = QPushButton('Abrir BD')
        open_db_btn.clicked.connect(self.open_database)
        db_layout.addWidget(open_db_btn)
        
        new_db_btn = QPushButton('Novo BD')
        new_db_btn.clicked.connect(self.create_new_database)
        db_layout.addWidget(new_db_btn)
        
        left_layout.addLayout(db_layout)
        
        # Database info
        self.db_info_label = QLabel('Nenhum banco carregado')
        left_layout.addWidget(self.db_info_label)
        
        # Tables list
        tables_label = QLabel('Tabelas:')
        tables_label.setFont(QFont('Segoe UI', 11, QFont.Bold))
        left_layout.addWidget(tables_label)
        
        self.tables_list = QListWidget()
        self.tables_list.itemClicked.connect(self.on_table_selected)
        left_layout.addWidget(self.tables_list)
        
        # Table buttons
        table_buttons_layout = QVBoxLayout()
        
        create_table_btn = QPushButton('Criar Tabela')
        create_table_btn.clicked.connect(self.create_table)
        table_buttons_layout.addWidget(create_table_btn)
        
        self.delete_table_btn = QPushButton('Deletar Tabela')
        self.delete_table_btn.clicked.connect(self.delete_table)
        self.delete_table_btn.setEnabled(False)
        table_buttons_layout.addWidget(self.delete_table_btn)
        
        export_btn = QPushButton('Exportar para SQL')
        export_btn.clicked.connect(self.export_database)
        table_buttons_layout.addWidget(export_btn)
        
        left_layout.addLayout(table_buttons_layout)
        left_layout.addStretch()
        
        # Right panel - Data operations
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Table data
        data_label = QLabel('Dados da Tabela:')
        data_label.setFont(QFont('Segoe UI', 11, QFont.Bold))
        right_layout.addWidget(data_label)
        
        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(0)
        right_layout.addWidget(self.table_widget)
        
        # Data buttons
        data_buttons_layout = QHBoxLayout()
        
        self.insert_btn = QPushButton('Inserir Linha')
        self.insert_btn.clicked.connect(self.insert_data)
        self.insert_btn.setEnabled(False)
        data_buttons_layout.addWidget(self.insert_btn)
        
        self.delete_row_btn = QPushButton('Deletar Linha')
        self.delete_row_btn.clicked.connect(self.delete_row)
        self.delete_row_btn.setEnabled(False)
        data_buttons_layout.addWidget(self.delete_row_btn)
        
        self.refresh_btn = QPushButton('Atualizar')
        self.refresh_btn.clicked.connect(self.refresh_table_data)
        self.refresh_btn.setEnabled(False)
        data_buttons_layout.addWidget(self.refresh_btn)
        
        right_layout.addLayout(data_buttons_layout)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
    
    def create_new_database(self):
        """Cria novo banco de dados"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Novo Banco de Dados',
            os.path.expanduser('~/Documentos'),
            'SQLite Database (*.db);;All Files (*)'
        )
        
        if file_path:
            try:
                self.db_manager = SQLDatabaseManager(file_path)
                self.db_path_label.setText(file_path)
                self.update_database_info()
                QMessageBox.information(self, 'Sucesso', 'Banco de dados criado!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao criar banco: {str(e)}')
    
    def open_database(self):
        """Abre um banco de dados existente"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Abrir Banco de Dados',
            os.path.expanduser('~/Documentos'),
            'SQLite Database (*.db);;All Files (*)'
        )
        
        if file_path:
            try:
                self.db_manager = SQLDatabaseManager(file_path)
                self.db_path_label.setText(file_path)
                self.update_database_info()
                self.refresh_tables_list()
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao abrir banco: {str(e)}')
    
    def update_database_info(self):
        """Atualiza informações do banco de dados"""
        try:
            if not self.db_manager:
                self.db_info_label.setText('Nenhum banco carregado')
                return
            
            info = self.db_manager.get_database_info()
            size_mb = info['size'] / (1024 * 1024)
            
            info_text = (
                f"Tabelas: {info['tables_count']} | "
                f"Linhas: {info['total_rows']} | "
                f"Tamanho: {size_mb:.2f} MB"
            )
            self.db_info_label.setText(info_text)
            self.refresh_tables_list()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao carregar informações: {str(e)}')
    
    def refresh_tables_list(self):
        """Atualiza lista de tabelas"""
        try:
            if not self.db_manager:
                return
            
            self.tables_list.clear()
            tables = self.db_manager.get_tables()
            
            for table in tables:
                self.tables_list.addItem(table)
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao listar tabelas: {str(e)}')
    
    def on_table_selected(self, item):
        """Quando uma tabela é selecionada"""
        table_name = item.text()
        self.current_table = table_name
        self.refresh_table_data()
        
        self.delete_table_btn.setEnabled(True)
        self.insert_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
    
    def refresh_table_data(self):
        """Atualiza dados da tabela selecionada"""
        try:
            if not self.current_table:
                return
            
            # Get schema
            schema = self.db_manager.get_table_schema(self.current_table)
            
            # Get data
            results = self.db_manager.execute_query(f'SELECT * FROM {self.current_table}')
            
            # Setup table
            self.table_widget.setColumnCount(len(schema))
            self.table_widget.setRowCount(len(results))
            
            headers = [col['name'] for col in schema]
            self.table_widget.setHorizontalHeaderLabels(headers)
            
            # Fill data
            for row_idx, row_data in enumerate(results):
                for col_idx, col_name in enumerate(headers):
                    item = QTableWidgetItem(str(row_data.get(col_name, '')))
                    self.table_widget.setItem(row_idx, col_idx, item)
            
            # Resize columns
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            self.delete_row_btn.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao carregar dados: {str(e)}')
    
    def create_table(self):
        """Cria nova tabela"""
        if not self.db_manager:
            QMessageBox.warning(self, 'Aviso', 'Abra ou crie um banco de dados primeiro')
            return
        
        dialog = CreateTableDialog(self)
        
        if dialog.exec_():
            try:
                table_name, columns = dialog.get_table_info()
                self.db_manager.create_table(table_name, columns)
                self.refresh_tables_list()
                QMessageBox.information(self, 'Sucesso', f'Tabela "{table_name}" criada!')
            except ValueError as e:
                QMessageBox.warning(self, 'Validação', str(e))
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao criar tabela: {str(e)}')
    
    def delete_table(self):
        """Deleta tabela selecionada"""
        if not self.current_table:
            return
        
        reply = QMessageBox.question(
            self,
            'Confirmar',
            f'Deseja deletar a tabela "{self.current_table}"?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.drop_table(self.current_table)
                self.current_table = None
                self.table_widget.setColumnCount(0)
                self.table_widget.setRowCount(0)
                self.refresh_tables_list()
                self.delete_table_btn.setEnabled(False)
                self.insert_btn.setEnabled(False)
                QMessageBox.information(self, 'Sucesso', 'Tabela deletada!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao deletar tabela: {str(e)}')
    
    def insert_data(self):
        """Insere dados na tabela"""
        if not self.current_table:
            return
        
        try:
            schema = self.db_manager.get_table_schema(self.current_table)
            
            dialog = InsertDataDialog(self.current_table, schema, self)
            
            if dialog.exec_():
                data = dialog.get_data()
                self.db_manager.insert_row(self.current_table, data)
                self.refresh_table_data()
                QMessageBox.information(self, 'Sucesso', 'Linha inserida!')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao inserir dados: {str(e)}')
    
    def delete_row(self):
        """Deleta linha selecionada"""
        current_row = self.table_widget.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, 'Aviso', 'Selecione uma linha para deletar')
            return
        
        reply = QMessageBox.question(
            self,
            'Confirmar',
            'Deseja deletar esta linha?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Get ID from first column (assuming it's ID)
                id_value = self.table_widget.item(current_row, 0).text()
                self.db_manager.delete_row(self.current_table, 'id = ?', (id_value,))
                self.refresh_table_data()
                QMessageBox.information(self, 'Sucesso', 'Linha deletada!')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao deletar linha: {str(e)}')
    
    def export_database(self):
        """Exporta banco de dados para arquivo SQL"""
        if not self.db_manager:
            QMessageBox.warning(self, 'Aviso', 'Nenhum banco carregado')
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Exportar Banco de Dados',
            os.path.expanduser('~/Documentos'),
            'SQL Files (*.sql);;All Files (*)'
        )
        
        if file_path:
            try:
                self.db_manager.export_to_sql(file_path)
                QMessageBox.information(self, 'Sucesso', f'Banco exportado para:\n{file_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Erro ao exportar: {str(e)}')
    
    def apply_styles(self):
        """Aplica stylesheet"""
        stylesheet = """
        QMainWindow {
            background-color: #FAFAFA;
        }
        
        QLabel {
            color: #263238;
            font-family: 'Segoe UI';
        }
        
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #B0BEC5;
            border-radius: 4px;
            padding: 6px;
            background-color: #FFFFFF;
            color: #263238;
            font-family: 'Segoe UI';
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #009688;
            background-color: #FFFFFF;
        }
        
        QPushButton {
            background-color: #009688;
            color: #FFFFFF;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            font-family: 'Segoe UI';
        }
        
        QPushButton:hover {
            background-color: #00796B;
        }
        
        QPushButton:pressed {
            background-color: #004D40;
        }
        
        QTableWidget {
            background-color: #FFFFFF;
            alternate-background-color: #F5F5F5;
            gridline-color: #B0BEC5;
            border: 1px solid #B0BEC5;
            border-radius: 4px;
            color: #263238;
        }
        
        QHeaderView::section {
            background-color: #009688;
            color: #FFFFFF;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        QListWidget {
            background-color: #FFFFFF;
            border: 1px solid #B0BEC5;
            border-radius: 4px;
            color: #263238;
        }
        
        QListWidget::item:selected {
            background-color: #009688;
            color: #FFFFFF;
        }
        
        QDialog {
            background-color: #FAFAFA;
        }
        """
        self.setStyleSheet(stylesheet)


def main():
    import sys
    app = __import__('PyQt5.QtWidgets', fromlist=['QApplication']).QApplication(sys.argv)
    window = SQLDatabaseGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
