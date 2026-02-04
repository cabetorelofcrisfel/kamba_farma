from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox,
    QFrame, QGridLayout, QAbstractItemView, QTextEdit, QGroupBox,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` and other top-level packages are importable
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.paths import DB_DIR
from database.db import get_db_path, connect


class EditProductDialog(QDialog):
    """Diálogo para editar campos principais do produto."""
    def __init__(self, produto_id, parent=None):
        super().__init__(parent)
        self.produto_id = produto_id
        self.setWindowTitle("✏️ Editar Produto")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #2c3e50;
                font-weight: 500;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit {
                padding: 8px;
                border: 1.5px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border-color: #3498db;
                background-color: #f8f9ff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #2c3e50;
            }
        """)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Cabeçalho do diálogo
        header = QLabel("Editar Informações do Produto")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setWeight(QFont.Bold)
        header.setFont(header_font)
        header.setStyleSheet("color: #2c3e50; padding-bottom: 10px; border-bottom: 2px solid #3498db;")
        layout.addWidget(header)

        # Área de rolagem para muitos campos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        form_layout = QVBoxLayout(content_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(15)

        # Grupo de informações básicas
        basic_group = QGroupBox("Informações Básicas")
        basic_layout = QGridLayout(basic_group)
        basic_layout.setContentsMargins(15, 20, 15, 15)
        basic_layout.setHorizontalSpacing(15)
        basic_layout.setVerticalSpacing(12)

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome comercial do produto")
        self.unidade = QLineEdit()
        self.unidade.setPlaceholderText("Ex: un, kg, ml")
        self.codigo_barras = QLineEdit()
        self.codigo_barras.setPlaceholderText("Código de barras (opcional)")

        basic_layout.addWidget(QLabel("Nome Comercial*:"), 0, 0)
        basic_layout.addWidget(self.nome, 0, 1)
        basic_layout.addWidget(QLabel("Unidade:"), 1, 0)
        basic_layout.addWidget(self.unidade, 1, 1)
        basic_layout.addWidget(QLabel("Código Barras:"), 2, 0)
        basic_layout.addWidget(self.codigo_barras, 2, 1)

        # Grupo de preços
        price_group = QGroupBox("Preços")
        price_layout = QGridLayout(price_group)
        price_layout.setContentsMargins(15, 20, 15, 15)
        price_layout.setHorizontalSpacing(15)
        price_layout.setVerticalSpacing(12)

        self.preco_venda = QDoubleSpinBox()
        self.preco_venda.setRange(0, 9999999)
        self.preco_venda.setDecimals(2)
        self.preco_venda.setPrefix("AOA ")
        self.preco_venda.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.preco_compra = QDoubleSpinBox()
        self.preco_compra.setRange(0, 9999999)
        self.preco_compra.setDecimals(2)
        self.preco_compra.setPrefix("AOA ")
        self.preco_compra.setButtonSymbols(QDoubleSpinBox.NoButtons)

        price_layout.addWidget(QLabel("Preço Venda*:"), 0, 0)
        price_layout.addWidget(self.preco_venda, 0, 1)
        price_layout.addWidget(QLabel("Preço Compra:"), 1, 0)
        price_layout.addWidget(self.preco_compra, 1, 1)

        # Grupo de estoque
        stock_group = QGroupBox("Controle de Estoque")
        stock_layout = QGridLayout(stock_group)
        stock_layout.setContentsMargins(15, 20, 15, 15)
        stock_layout.setHorizontalSpacing(15)
        stock_layout.setVerticalSpacing(12)

        self.stock = QSpinBox()
        self.stock.setRange(0, 9999999)
        self.stock.setButtonSymbols(QSpinBox.NoButtons)
        self.stock_minimo = QSpinBox()
        self.stock_minimo.setRange(0, 9999999)
        self.stock_minimo.setButtonSymbols(QSpinBox.NoButtons)

        stock_layout.addWidget(QLabel("Stock Atual:"), 0, 0)
        stock_layout.addWidget(self.stock, 0, 1)
        stock_layout.addWidget(QLabel("Stock Mínimo:"), 1, 0)
        stock_layout.addWidget(self.stock_minimo, 1, 1)

        # Grupo de observações
        obs_group = QGroupBox("Observações")
        obs_layout = QVBoxLayout(obs_group)
        obs_layout.setContentsMargins(15, 20, 15, 15)
        
        self.descricao = QTextEdit()
        self.descricao.setPlaceholderText("Descrição adicional do produto...")
        self.descricao.setMaximumHeight(80)
        obs_layout.addWidget(self.descricao)

        # Adicionar grupos ao layout
        form_layout.addWidget(basic_group)
        form_layout.addWidget(price_group)
        form_layout.addWidget(stock_group)
        form_layout.addWidget(obs_group)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Botões de ação
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        cancel = QPushButton("❌ Cancelar")
        cancel.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border: 1.5px solid #dee2e6;
                border-radius: 6px;
                background-color: #f8f9fa;
                font-weight: 600;
                color: #6c757d;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #ced4da;
            }
        """)
        cancel.clicked.connect(self.reject)

        save = QPushButton("💾 Salvar Alterações")
        save.setStyleSheet("""
            QPushButton {
                padding: 10px 25px;
                border: none;
                border-radius: 6px;
                background-color: #28a745;
                font-weight: 600;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        save.clicked.connect(self._save)

        button_layout.addWidget(cancel)
        button_layout.addWidget(save)
        layout.addLayout(button_layout)

    def _load(self):
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT * FROM produtos WHERE id = ?", (self.produto_id,))
            r = cur.fetchone()
            conn.close()
            if not r:
                QMessageBox.warning(self, "Erro", "Produto não encontrado")
                self.reject()
                return

            self.nome.setText(r.get('nome_comercial', '') or '')
            self.preco_venda.setValue(r.get('preco_venda', 0.0) or 0.0)
            self.preco_compra.setValue(r.get('preco_compra', 0.0) or 0.0)
            self.stock.setValue(r.get('stock', 0) or 0)
            self.stock_minimo.setValue(r.get('stock_minimo', 0) or 0)
            self.unidade.setText(r.get('unidade', '') or '')
            self.codigo_barras.setText(r.get('codigo_barras', '') or '')
            self.descricao.setText(r.get('descricao', '') or '')

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produto: {e}")
            self.reject()

    def _save(self):
        if not self.nome.text().strip():
            QMessageBox.warning(self, "Aviso", "O nome do produto é obrigatório.")
            return
            
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute(
                """UPDATE produtos SET 
                   nome_comercial=?, preco_venda=?, preco_compra=?, stock=?, 
                   stock_minimo=?, unidade=?, codigo_barras=?, descricao=? 
                   WHERE id=?""",
                (
                    self.nome.text().strip(),
                    float(self.preco_venda.value()),
                    float(self.preco_compra.value()),
                    int(self.stock.value()),
                    int(self.stock_minimo.value()),
                    self.unidade.text().strip() or None,
                    self.codigo_barras.text().strip() or None,
                    self.descricao.toPlainText().strip() or None,
                    self.produto_id
                )
            )
            conn.commit()
            conn.close()
            
            QMessageBox.information(
                self, 
                "✅ Sucesso", 
                "Produto atualizado com sucesso!"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "❌ Erro", f"Erro ao salvar: {str(e)}")


class ProdutosView(QWidget):
    """View para listar/gerir produtos com opção de editar e deletar."""

    # Emite quando o usuário clicar em "Adicionar Produto" na própria view
    open_add = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_products()

    def refresh(self):
        """Compatibilidade: método que recarrega os produtos a partir do DB."""
        try:
            self.load_products()
        except Exception:
            pass

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Configurar cor de fundo
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f8f9fa"))
        self.setPalette(palette)

        # Cabeçalho SIMPLIFICADO (sem frame)
        header_layout = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        title = QLabel("📦 Gestão de Produtos")
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        
        subtitle = QLabel("Gerencie seu inventário de produtos")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #7f8c8d;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(0)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Botão de adicionar produto
        add_btn = QPushButton("➕ Adicionar Produto")
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        # Ao clicar, emitimos um sinal para que o container (ProdutoPage) possa abrir a view de Adicionar
        add_btn.clicked.connect(lambda: self.open_add.emit())
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)

        # Filtros (frame mantido para estilo)
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #dee2e6;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Pesquisar por nome, código...")
        search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1.5px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                width: 300px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        filter_combo = QComboBox()
        filter_combo.addItems(["Todos", "Em estoque", "Baixo estoque", "Sem estoque"])
        filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 15px;
                border: 1.5px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
        """)
        
        filter_layout.addWidget(search_input)
        filter_layout.addWidget(filter_combo)
        filter_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        refresh_btn.clicked.connect(self.load_products)
        filter_layout.addWidget(refresh_btn)
        
        layout.addWidget(filter_frame)

        # Tabela de produtos - SEM FRAME para melhor dimensionamento
        self.table = QTableWidget()
        self.table.setMinimumHeight(400)  # Aumentado para melhor visibilidade
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Preço Venda", "Stock", "Status", "Editar", "Excluir"])
        
        # Configurar cabeçalho - AUMENTADO as larguras das colunas
        header = self.table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: 600;
                color: #2c3e50;
                font-size: 13px;
            }
        """)
        header.setDefaultAlignment(Qt.AlignLeft)
        header.setSectionResizeMode(QHeaderView.Interactive)  # Mudado para Interactive
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nome estica
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        
        # AUMENTADO as larguras para melhor visibilidade
        self.table.setColumnWidth(0, 80)    # ID
        self.table.setColumnWidth(2, 150)   # Preço Venda
        self.table.setColumnWidth(3, 120)   # Stock
        self.table.setColumnWidth(4, 140)   # Status
        self.table.setColumnWidth(5, 100)   # Editar
        self.table.setColumnWidth(6, 100)   # Excluir
        
        # Configurar aparência da tabela
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 12px;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
        """)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Aumentar a altura das linhas para botões ficarem visíveis
        self.table.verticalHeader().setDefaultSectionSize(55)
        
        layout.addWidget(self.table, 1)  # O fator 1 faz expandir

        # Rodapé com estatísticas
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 12px 20px;
                border: 1px solid #dee2e6;
            }
        """)
        footer_layout = QHBoxLayout(footer)
        
        self.stats_label = QLabel("Carregando estatísticas...")
        self.stats_label.setStyleSheet("color: #6c757d; font-size: 13px;")
        
        footer_layout.addWidget(self.stats_label)
        footer_layout.addStretch()
        
        export_btn = QPushButton("📤 Exportar Lista")
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 15px;
                background-color: transparent;
                color: #3498db;
                border: 1.5px solid #3498db;
                border-radius: 6px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
        """)
        footer_layout.addWidget(export_btn)
        
        layout.addWidget(footer)

    def load_products(self):
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nome_comercial, preco_venda, stock, stock_minimo 
                FROM produtos 
                WHERE ativo=1 
                ORDER BY nome_comercial
            """)
            rows = cur.fetchall()
            conn.close()

            self.table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                # ID
                id_item = QTableWidgetItem(str(r['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 0, id_item)

                # Nome
                nome_item = QTableWidgetItem(r['nome_comercial'] or '')
                nome_item.setToolTip(r['nome_comercial'] or '')
                self.table.setItem(i, 1, nome_item)

                # Preço
                preco_item = QTableWidgetItem(f"AOA {(r['preco_venda'] or 0):,.2f}")
                preco_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, 2, preco_item)

                # Stock
                stock = r['stock'] or 0
                stock_minimo = r['stock_minimo'] or 0
                stock_item = QTableWidgetItem(f"{stock}")
                stock_item.setTextAlignment(Qt.AlignCenter)
                
                if stock == 0:
                    stock_item.setForeground(QColor("#dc3545"))
                elif stock <= stock_minimo:
                    stock_item.setForeground(QColor("#ffc107"))
                else:
                    stock_item.setForeground(QColor("#28a745"))
                    
                self.table.setItem(i, 3, stock_item)

                # Status
                status_widget = QWidget()
                status_layout = QHBoxLayout(status_widget)
                status_layout.setContentsMargins(5, 2, 5, 2)  # Reduzido para caber melhor
                status_layout.setAlignment(Qt.AlignCenter)
                
                status_label = QLabel()
                status_label.setStyleSheet("""
                    QLabel {
                        padding: 6px 12px;
                        border-radius: 12px;
                        font-weight: 600;
                        font-size: 11px;
                    }
                """)
                
                if stock == 0:
                    status_label.setText("Sem Estoque")
                    status_label.setStyleSheet(status_label.styleSheet() + "background-color: #f8d7da; color: #721c24;")
                elif stock <= stock_minimo:
                    status_label.setText("Baixo Estoque")
                    status_label.setStyleSheet(status_label.styleSheet() + "background-color: #fff3cd; color: #856404;")
                else:
                    status_label.setText("Em Estoque")
                    status_label.setStyleSheet(status_label.styleSheet() + "background-color: #d4edda; color: #155724;")
                
                status_layout.addWidget(status_label)
                self.table.setCellWidget(i, 4, status_widget)

                # Botão Editar - AUMENTADO o tamanho
                edit_btn = QPushButton("✏️ Editar")
                edit_btn.setToolTip("Editar produto")
                edit_btn.setFixedHeight(35)  # Altura fixa
                edit_btn.setStyleSheet("""
                    QPushButton {
                        padding: 6px 12px;
                        background-color: #e3f2fd;
                        border: 1.5px solid #bbdefb;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: 500;
                        color: #1565c0;
                    }
                    QPushButton:hover {
                        background-color: #bbdefb;
                        border-color: #90caf9;
                    }
                    QPushButton:pressed {
                        background-color: #90caf9;
                    }
                """)
                edit_btn.clicked.connect(lambda _, pid=r['id']: self._on_edit(pid))
                self.table.setCellWidget(i, 5, edit_btn)

                # Botão Excluir - AUMENTADO o tamanho
                delete_btn = QPushButton("🗑️ Excluir")
                delete_btn.setToolTip("Excluir produto")
                delete_btn.setFixedHeight(35)  # Altura fixa
                delete_btn.setStyleSheet("""
                    QPushButton {
                        padding: 6px 12px;
                        background-color: #fdecea;
                        border: 1.5px solid #fcd9d5;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: 500;
                        color: #c62828;
                    }
                    QPushButton:hover {
                        background-color: #fcd9d5;
                        border-color: #f9c6c1;
                    }
                    QPushButton:pressed {
                        background-color: #f9c6c1;
                    }
                """)
                delete_btn.clicked.connect(lambda _, pid=r['id']: self._on_delete(pid))
                self.table.setCellWidget(i, 6, delete_btn)

          

        except Exception as e:
            QMessageBox.critical(self, "❌ Erro", f"Erro ao carregar produtos: {e}")

    def _on_delete(self, produto_id):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("⚠️ Confirmar Exclusão")
        msg_box.setText("Deseja realmente desativar este produto?")
        msg_box.setInformativeText("O produto será marcado como inativo e não aparecerá mais no catálogo.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Estilizar a caixa de mensagem
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #2c3e50;
            }
        """)
        
        yes_button = msg_box.button(QMessageBox.Yes)
        yes_button.setText("Sim, Excluir")
        yes_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        no_button = msg_box.button(QMessageBox.No)
        no_button.setText("Cancelar")
        no_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        if msg_box.exec_() != QMessageBox.Yes:
            return
            
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            cur.execute("UPDATE produtos SET ativo=0 WHERE id=?", (produto_id,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(
                self, 
                "✅ Sucesso", 
                "Produto desativado com sucesso!"
            )
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "❌ Erro", f"Erro ao excluir produto: {e}")

    def _on_edit(self, produto_id):
        dlg = EditProductDialog(produto_id, self)
        dlg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #2c3e50;
            }
        """)
        if dlg.exec_() == QDialog.Accepted:
            self.load_products()