from pathlib import Path
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QWidget as QWidgetLocal,
    QGridLayout, QFrame, QSizePolicy, QSpacerItem, QHBoxLayout,
    QPushButton, QMessageBox, QProgressBar, QGroupBox, QFormLayout,
    QLineEdit, QComboBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QBrush

# Ensure project root is on sys.path so `src` and other top-level packages are importable
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.paths import DB_DIR
from database.db import get_db_path, connect

# Paleta de cores moderna
PRIMARY_COLOR = "#4A6CF7"
SECONDARY_COLOR = "#10B981"
DANGER_COLOR = "#EF4444"
WARNING_COLOR = "#F59E0B"
INFO_COLOR = "#3B82F6"
BG_COLOR = "#F8FAFD"
CARD_BG = "#FFFFFF"
BORDER_COLOR = "#E8EEF5"
TEXT_PRIMARY = "#1A1D29"
TEXT_SECONDARY = "#6B7280"
TEXT_LIGHT = "#9CA3AF"
SUCCESS_COLOR = "#10B981"


class ProdutosView(QWidget):
    """Visualização moderna de produtos com baixo stock."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_low_stock()
        
        # Configurar fundo
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(BG_COLOR))
        self.setPalette(palette)

    def _setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Área de rolagem
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #F3F4F6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #D1D5DB;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9CA3AF;
            }
        """)
        
        # Container principal
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(25)
        
        # Cabeçalho
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {BORDER_COLOR};
                padding: 24px;
            }}
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(12)
        
        title = QLabel("⚠️ Produtos com Baixo Stock")
        title_font = QFont("Segoe UI", 22, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        
        # subtitle removed per request
        
        # Estatísticas
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.stats_total, self.stats_total_value = self._create_stat_card("📊 Total Produtos", "0", INFO_COLOR)
        self.stats_critical, self.stats_critical_value = self._create_stat_card("🔴 Crítico", "0", DANGER_COLOR)
        self.stats_warning, self.stats_warning_value = self._create_stat_card("🟠 Atenção", "0", WARNING_COLOR)
        self.stats_low, self.stats_low_value = self._create_stat_card("🟡 Baixo", "0", "#FBBF24")

        stats_layout.addWidget(self.stats_total)
        stats_layout.addWidget(self.stats_critical)
        stats_layout.addWidget(self.stats_warning)
        stats_layout.addWidget(self.stats_low)
        stats_layout.addStretch()
        
        # Filtros rápidos
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        filter_label = QLabel("Filtrar por urgência:")
        filter_label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600;")
        
        self.filter_critical = QPushButton("🔴 Crítico")
        self.filter_warning = QPushButton("🟠 Atenção")
        self.filter_low = QPushButton("🟡 Baixo")
        self.filter_all = QPushButton("📋 Todos")
        
        for btn in [self.filter_critical, self.filter_warning, self.filter_low, self.filter_all]:
            btn.setMinimumHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CARD_BG};
                    color: {TEXT_SECONDARY};
                    border: 1.5px solid {BORDER_COLOR};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: #F3F4F6;
                }}
                QPushButton:checked {{
                    background-color: {PRIMARY_COLOR};
                    color: white;
                    border-color: {PRIMARY_COLOR};
                }}
            """)
            btn.setCheckable(True)
        
        self.filter_all.setChecked(True)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_critical)
        filter_layout.addWidget(self.filter_warning)
        filter_layout.addWidget(self.filter_low)
        filter_layout.addWidget(self.filter_all)
        filter_layout.addStretch()
        
        # Botão de atualizar
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #3B52CC;
            }}
        """)
        refresh_btn.clicked.connect(self._load_low_stock)
        
        filter_layout.addWidget(refresh_btn)
        
        header_layout.addWidget(title)
        header_layout.addLayout(stats_layout)
        header_layout.addLayout(filter_layout)
        container_layout.addWidget(header_frame)
        
        # Container dos produtos
        products_frame = QFrame()
        products_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 12px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        products_layout = QVBoxLayout(products_frame)
        products_layout.setContentsMargins(0, 0, 0, 0)
        
        # Cabeçalho da lista
        list_header = QFrame()
        list_header.setFixedHeight(50)
        list_header.setStyleSheet(f"background-color: {CARD_BG}; border-bottom: 1px solid {BORDER_COLOR};")
        
        header_inner = QHBoxLayout(list_header)
        header_inner.setContentsMargins(20, 0, 20, 0)
        
        list_title = QLabel("Produtos que necessitam de atenção")
        list_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        """)
        
        header_inner.addWidget(list_title)
        header_inner.addStretch()
        
        # Legenda
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(15)
        
        critical_legend = QLabel("🔴 Estoque ≤ 20% do mínimo")
        critical_legend.setStyleSheet(f"color: {DANGER_COLOR}; font-size: 12px;")
        
        warning_legend = QLabel("🟠 Estoque ≤ 50% do mínimo")
        warning_legend.setStyleSheet(f"color: {WARNING_COLOR}; font-size: 12px;")
        
        low_legend = QLabel("🟡 Estoque ≤ 100% do mínimo")
        low_legend.setStyleSheet("color: #FBBF24; font-size: 12px;")
        
        legend_layout.addWidget(critical_legend)
        legend_layout.addWidget(warning_legend)
        legend_layout.addWidget(low_legend)
        legend_layout.addStretch()
        
        header_inner.addLayout(legend_layout)
        products_layout.addWidget(list_header)
        
        # Grid de produtos
        self.container = QWidgetLocal()
        self.container.setStyleSheet("background-color: transparent;")
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.grid.setHorizontalSpacing(20)
        self.grid.setVerticalSpacing(20)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Configurar colunas
        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 0)
        self.grid.setColumnStretch(2, 0)
        self.grid.setColumnStretch(3, 0)
        
        products_layout.addWidget(self.container)
        container_layout.addWidget(products_frame)
        
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)
        
        # Conectar filtros
        for btn in [self.filter_critical, self.filter_warning, self.filter_low, self.filter_all]:
            btn.clicked.connect(self._apply_filter)

    def _create_stat_card(self, title, value, color):
        """Cria um card de estatística."""
        card = QFrame()
        card.setMinimumWidth(180)
        card.setMaximumWidth(220)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
                padding: 16px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 13px;
            color: {TEXT_SECONDARY};
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {color};
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Return both card and its value label so callers can update values directly
        return card, value_label

    def _create_product_card(self, product_data):
        """Cria um cartão de produto com informações detalhadas."""
        name = product_data['nome_comercial'] or '-'
        stock = product_data['stock'] or 0
        stock_minimo = product_data['stock_minimo'] or 0
        photo_bytes = product_data['foto']
        
        # Determinar nível de urgência
        if stock_minimo == 0:
            # Se não tem mínimo definido, usar padrão
            if stock == 0:
                urgency_level = "critical"
                bg_color = "#FEF2F2"
                border_color = DANGER_COLOR
                percent = 0
            elif stock <= 2:
                urgency_level = "critical"
                bg_color = "#FEF2F2"
                border_color = DANGER_COLOR
                percent = (stock / 5) * 100 if stock > 0 else 0
            elif stock <= 5:
                urgency_level = "warning"
                bg_color = "#FFFBEB"
                border_color = WARNING_COLOR
                percent = (stock / 5) * 100
            else:
                urgency_level = "low"
                bg_color = "#FEFCE8"
                border_color = "#FBBF24"
                percent = 100
        else:
            # Com stock mínimo definido
            percent = (stock / stock_minimo) * 100 if stock_minimo > 0 else 0
            
            if stock == 0:
                urgency_level = "critical"
                bg_color = "#FEF2F2"
                border_color = DANGER_COLOR
            elif percent <= 20:
                urgency_level = "critical"
                bg_color = "#FEF2F2"
                border_color = DANGER_COLOR
            elif percent <= 50:
                urgency_level = "warning"
                bg_color = "#FFFBEB"
                border_color = WARNING_COLOR
            else:
                urgency_level = "low"
                bg_color = "#FEFCE8"
                border_color = "#FBBF24"
        
        # Card principal
        card = QFrame()
        card.setFixedSize(280, 320)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 15px;
                border: 2px solid {border_color};
            }}
            QFrame:hover {{
                border: 2px solid {PRIMARY_COLOR};
                background-color: {bg_color}DD;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)

        # Container da imagem
        img_container = QFrame()
        img_container.setFixedSize(100, 100)
        img_container.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(5, 5, 5, 5)
        
        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        img.setFixedSize(90, 90)
        
        if photo_bytes:
            pix = QPixmap()
            if pix.loadFromData(photo_bytes):
                pix = pix.scaled(85, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img.setPixmap(pix)
            else:
                img.setText("📦")
                img.setStyleSheet("font-size: 36px; color: #9CA3AF;")
        else:
            img.setText("📦")
            img.setStyleSheet("font-size: 36px; color: #9CA3AF;")
        
        img_layout.addWidget(img)
        
        # Nome do produto
        name_label = QLabel(name)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(50)
        name_label.setStyleSheet(f"""
            QLabel {{
                font-weight: 700;
                font-size: 16px;
                color: {TEXT_PRIMARY};
            }}
        """)
        
        # Informações de stock
        stock_container = QFrame()
        stock_container.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid {BORDER_COLOR};
                padding: 10px;
            }}
        """)
        
        stock_layout = QVBoxLayout(stock_container)
        stock_layout.setSpacing(8)
        stock_layout.setContentsMargins(10, 10, 10, 10)
        
        # Barra de progresso
        progress_label = QLabel("Nível do Stock:")
        progress_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(percent))
        
        if urgency_level == "critical":
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {DANGER_COLOR}40;
                    border-radius: 5px;
                    text-align: center;
                    height: 12px;
                }}
                QProgressBar::chunk {{
                    background-color: {DANGER_COLOR};
                    border-radius: 5px;
                }}
            """)
        elif urgency_level == "warning":
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {WARNING_COLOR}40;
                    border-radius: 5px;
                    text-align: center;
                    height: 12px;
                }}
                QProgressBar::chunk {{
                    background-color: {WARNING_COLOR};
                    border-radius: 5px;
                }}
            """)
        else:
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #FBBF2440;
                    border-radius: 5px;
                    text-align: center;
                    height: 12px;
                }}
                QProgressBar::chunk {{
                    background-color: #FBBF24;
                    border-radius: 5px;
                }}
            """)
        
        # Valores numéricos
        values_layout = QHBoxLayout()
        
        stock_current = QLabel(f"📦 {stock}")
        stock_current.setStyleSheet(f"""
            QLabel {{
                font-weight: 700;
                font-size: 18px;
                color: {border_color};
            }}
        """)
        
        stock_min = QLabel(f"🎯 {stock_minimo}")
        stock_min.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                font-size: 16px;
                color: {TEXT_SECONDARY};
            }}
        """)
        
        values_layout.addWidget(stock_current)
        values_layout.addStretch()
        values_layout.addWidget(stock_min)
        
        stock_layout.addWidget(progress_label)
        stock_layout.addWidget(progress_bar)
        stock_layout.addLayout(values_layout)
        
        # Botão de ação
        action_btn = QPushButton("📝 Repor Stock")
        action_btn.setCursor(Qt.PointingHandCursor)
        action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #3B52CC;
            }}
        """)
        action_btn.clicked.connect(lambda: self._on_reorder(product_data['id'], name))
        
        # Adicionar widgets ao layout
        layout.addWidget(img_container, 0, Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(stock_container)
        layout.addWidget(action_btn)
        
        # Armazenar dados de urgência
        card.urgency_level = urgency_level
        
        return card

    def _load_low_stock(self):
        """Carrega produtos com baixo stock."""
        try:
            db_path = get_db_path(DB_DIR)
            conn = connect(db_path)
            cur = conn.cursor()
            
            # Consulta para produtos com baixo stock
            cur.execute("""
                SELECT id, nome_comercial, foto, stock, COALESCE(stock_minimo, 0) as stock_minimo
                FROM produtos
                WHERE ativo=1 AND (
                    (COALESCE(stock_minimo,0) > 0 AND stock <= stock_minimo)
                    OR (COALESCE(stock_minimo,0) = 0 AND stock <= 5)
                )
                ORDER BY 
                    CASE 
                        WHEN stock = 0 THEN 1
                        WHEN stock_minimo > 0 AND stock <= stock_minimo * 0.2 THEN 2
                        WHEN stock_minimo > 0 AND stock <= stock_minimo * 0.5 THEN 3
                        ELSE 4
                    END,
                    stock ASC,
                    nome_comercial
            """)
            rows = cur.fetchall()
            conn.close()

            # Limpar grid existente
            for i in reversed(range(self.grid.count())):
                w = self.grid.itemAt(i).widget()
                if w:
                    w.setParent(None)

            if not rows:
                # Mensagem quando não há produtos com baixo stock
                no_products = QLabel("✅ Todos os produtos estão com stock adequado!")
                no_products.setAlignment(Qt.AlignCenter)
                no_products_font = QFont()
                no_products_font.setPointSize(16)
                no_products.setFont(no_products_font)
                no_products.setStyleSheet(f"""
                    QLabel {{
                        color: {SUCCESS_COLOR};
                        padding: 50px;
                        background-color: white;
                        border-radius: 15px;
                        border: 2px solid #A7F3D0;
                    }}
                """)
                self.grid.addWidget(no_products, 0, 0, 1, 4)
                
                # Atualizar estatísticas
                self._update_stats([], rows)
                return

            # Armazenar todos os produtos para filtragem
            self.all_products = rows
            
            # Aplicar filtro atual
            self._apply_filter()
            
        except Exception as e:
            # Mensagem de erro melhorada
            error_container = QFrame()
            error_container.setStyleSheet(f"""
                QFrame {{
                    background-color: #FEF2F2;
                    border-radius: 10px;
                    border: 1px solid {DANGER_COLOR}40;
                    padding: 20px;
                }}
            """)
            error_layout = QVBoxLayout(error_container)
            
            error_icon = QLabel("🚨")
            error_icon.setAlignment(Qt.AlignCenter)
            error_icon.setStyleSheet("font-size: 32px; margin-bottom: 10px;")
            
            error_label = QLabel(f"Erro ao carregar produtos:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setWordWrap(True)
            error_label.setStyleSheet(f"color: {DANGER_COLOR}; font-weight: 500;")
            
            error_layout.addWidget(error_icon)
            error_layout.addWidget(error_label)
            
            self.grid.addWidget(error_container, 0, 0, 1, 4)

    def _apply_filter(self):
        """Aplica o filtro selecionado."""
        # Desmarcar todos os botões exceto o clicado
        sender = self.sender()
        for btn in [self.filter_critical, self.filter_warning, self.filter_low, self.filter_all]:
            if btn != sender:
                btn.setChecked(False)
        
        # Se nenhum está marcado, marcar "Todos"
        if not any([self.filter_critical.isChecked(), self.filter_warning.isChecked(), 
                    self.filter_low.isChecked(), self.filter_all.isChecked()]):
            self.filter_all.setChecked(True)
        
        # Limpar grid
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)
        
        if not hasattr(self, 'all_products'):
            return
        
        # Filtrar produtos
        filtered_products = []
        for product in self.all_products:
            card = self._create_product_card(product)
            
            if self.filter_critical.isChecked() and card.urgency_level == "critical":
                filtered_products.append((product, card))
            elif self.filter_warning.isChecked() and card.urgency_level == "warning":
                filtered_products.append((product, card))
            elif self.filter_low.isChecked() and card.urgency_level == "low":
                filtered_products.append((product, card))
            elif self.filter_all.isChecked():
                filtered_products.append((product, card))
        
        # Atualizar estatísticas com produtos filtrados
        self._update_stats(filtered_products, self.all_products)
        
        if not filtered_products:
            # Mensagem quando não há produtos no filtro
            no_filtered = QLabel(f"Nenhum produto encontrado para o filtro selecionado")
            no_filtered.setAlignment(Qt.AlignCenter)
            no_filtered_font = QFont()
            no_filtered_font.setPointSize(14)
            no_filtered.setFont(no_filtered_font)
            no_filtered.setStyleSheet(f"""
                QLabel {{
                    color: {TEXT_SECONDARY};
                    padding: 50px;
                    background-color: white;
                    border-radius: 15px;
                    border: 2px solid {BORDER_COLOR};
                }}
            """)
            self.grid.addWidget(no_filtered, 0, 0, 1, 4)
            return
        
        # Adicionar produtos filtrados ao grid
        cols = 3
        row = 0
        col = 0
        
        for product, card in filtered_products:
            self.grid.addWidget(card, row, col)
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        # Adicionar espaçador para empurrar cards para esquerda
        if col > 0:
            for c in range(col, cols):
                spacer = QWidgetLocal()
                spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                self.grid.addWidget(spacer, row, c)
        
        # Adicionar coluna de expansão
        self.grid.setColumnStretch(cols, 1)

    def _update_stats(self, filtered_products, all_products):
        """Atualiza as estatísticas."""
        total_all = len(all_products)
        
        # Contar por nível de urgência
        critical = warning = low = 0
        
        for product in all_products:
            stock = product['stock'] or 0
            stock_minimo = product['stock_minimo'] or 0
            
            if stock_minimo == 0:
                if stock == 0 or stock <= 2:
                    critical += 1
                elif stock <= 5:
                    warning += 1
                else:
                    low += 1
            else:
                percent = (stock / stock_minimo) * 100 if stock_minimo > 0 else 0
                if stock == 0 or percent <= 20:
                    critical += 1
                elif percent <= 50:
                    warning += 1
                else:
                    low += 1
        
        total_filtered = len(filtered_products)
        
        # Atualizar cards de estatística usando as referências diretas
        try:
            self.stats_total_value.setText(str(total_filtered if filtered_products else total_all))
        except Exception:
            pass
        try:
            self.stats_critical_value.setText(str(critical))
        except Exception:
            pass
        try:
            self.stats_warning_value.setText(str(warning))
        except Exception:
            pass
        try:
            self.stats_low_value.setText(str(low))
        except Exception:
            pass

    def _on_reorder(self, product_id, product_name):
        """Abre diálogo para reposição de stock."""
        reply = QMessageBox.question(
            self,
            "Repor Stock",
            f"Deseja repor o stock do produto '{product_name}'?\n\n"
            "Esta ação abrirá a tela de adicionar novo lote.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Aqui você pode emitir um sinal para abrir a tela de adicionar lote
            # com o produto pré-selecionado
            QMessageBox.information(
                self,
                "Ação necessária",
                "Por favor, vá para a tela 'Adicionar Lote' para registrar a reposição."
            )


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ProdutosView()
    window.resize(1200, 800)
    window.setWindowTitle("Produtos com Baixo Stock - Kamba Farma")
    window.show()
    
    sys.exit(app.exec_())
    