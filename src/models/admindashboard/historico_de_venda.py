"""
Módulo de Histórico de Vendas – Kamba Farma

Responsável por:
- Buscar vendas no banco de dados SQLite
- Agrupar itens por venda
- Exibir histórico em tabela (PyQt5)
- Gerar fatura em PDF
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QApplication, QFileDialog, QDialog, QDialogButtonBox,
    QSpacerItem, QSizePolicy, QDateEdit, QComboBox, QGroupBox,
    QFormLayout, QFrame, QProgressDialog
)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt5.QtGui import QTextDocument, QFont, QIcon, QColor, QBrush
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog


# =========================================================
# Localização do banco de dados
# =========================================================
def _find_db_file() -> Optional[Path]:
    root = Path(__file__).resolve()
    for _ in range(8):
        db_dir = root / "database"
        if db_dir.exists():
            db_file = db_dir / "kamba_farma.db"
            return db_file if db_file.exists() else None
        root = root.parent
    return None


# =========================================================
# Consulta do histórico de vendas
# =========================================================
def obter_historico(
    venda_id: Optional[int] = None,
    limite: int = 100,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    cliente: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], float]:
    """Retorna histórico de vendas e total geral"""
    db_file = _find_db_file()
    if not db_file:
        return [], 0.0

    conn = None
    try:
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        where_conditions = []
        params = []

        if venda_id is not None:
            where_conditions.append("v.id = ?")
            params.append(venda_id)

        if data_inicio:
            where_conditions.append("DATE(v.data_venda) >= ?")
            params.append(data_inicio)

        if data_fim:
            where_conditions.append("DATE(v.data_venda) <= ?")
            params.append(data_fim)

        if cliente:
            where_conditions.append("""
                EXISTS (
                    SELECT 1 FROM historico_compra hc 
                    WHERE ABS(strftime('%s', hc.tempo_compra) - strftime('%s', v.data_venda)) < 10 
                    AND hc.comprador_nome LIKE ?
                )
            """)
            params.append(f"%{cliente}%")

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # Primeiro, contar total de vendas
        cur.execute(f"SELECT COUNT(*) as total FROM vendas v {where_clause}", params)
        total_vendas = cur.fetchone()["total"]

        # Buscar vendas com limite
        cur.execute(
            f"""
            SELECT v.id, v.data_venda, v.total
            FROM vendas v
            {where_clause}
            ORDER BY v.data_venda DESC
            LIMIT ?
            """,
            (*params, limite)
        )

        vendas = cur.fetchall()
        resultado = []
        total_geral = 0.0

        for v in vendas:
            cur.execute(
                """
                SELECT
                    iv.produto_id,
                    p.nome_comercial AS produto_nome,
                    iv.quantidade,
                    iv.preco_unitario,
                    iv.subtotal
                FROM itens_venda iv
                LEFT JOIN produtos p ON p.id = iv.produto_id
                WHERE iv.venda_id = ?
                """,
                (v["id"],)
            )

            itens = cur.fetchall()
            produtos = []
            qtd_total = 0

            for it in itens:
                qtd = it["quantidade"] or 0
                qtd_total += qtd
                produtos.append({
                    "produto_id": it["produto_id"],
                    "produto_nome": it["produto_nome"],
                    "quantidade": qtd,
                    "preco_unitario": it["preco_unitario"],
                    "subtotal": it["subtotal"],
                })

            comprador = None
            try:
                cur.execute(
                    """
                    SELECT comprador_nome
                    FROM historico_compra
                    WHERE ABS(
                        strftime('%s', tempo_compra) -
                        strftime('%s', ?)
                    ) < 10
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (v["data_venda"],)
                )
                row = cur.fetchone()
                if row:
                    comprador = row["comprador_nome"]
            except sqlite3.Error:
                comprador = None

            venda_total = v["total"] or 0.0
            total_geral += venda_total
            
            resultado.append({
                "venda_id": v["id"],
                "data": v["data_venda"],
                "total": venda_total,
                "quantidade_total": qtd_total,
                "produtos": produtos,
                "comprador": comprador,
                "total_vendas": total_vendas
            })

        return resultado, total_geral

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
        return [], 0.0

    finally:
        if conn:
            conn.close()


# =========================================================
# Interface gráfica – Histórico de Vendas
# =========================================================
class HistoricoVendaView(QWidget):
    """Interface moderna para histórico de vendas"""
    
    # Sinal para atualização em tempo real
    atualizado = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Histórico de Vendas - Kamba Farma")
        self.resize(1400, 800)
        self.setStyleSheet(self._get_stylesheet())
        
        # Variáveis de estado
        self.vendas = []
        self.total_geral = 0.0
        self.filtro_ativo = False
        
        # Timer para atualização automática
        self.timer = QTimer()
        self.timer.timeout.connect(self._atualizar_automaticamente)
        self.timer.start(30000)  # Atualiza a cada 30 segundos
        
        self._build_ui()
        self.load_history()

    def _get_stylesheet(self) -> str:
        """Retorna o stylesheet CSS para a interface"""
        return """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton#btnPdf {
                background-color: #2196F3;
            }
            
            QPushButton#btnPdf:hover {
                background-color: #1976D2;
            }
            
            QPushButton#btnReset {
                background-color: #f44336;
            }
            
            QPushButton#btnReset:hover {
                background-color: #d32f2f;
            }
            
            QLineEdit, QDateEdit, QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
                border: 1px solid #4CAF50;
                outline: none;
            }
            
            QTableWidget {
                gridline-color: #e0e0e0;
                selection-background-color: #e3f2fd;
                alternate-background-color: #f9f9f9;
            }
            
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: 600;
            }
            
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: 600;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QLabel#title {
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
                margin: 0;
                padding: 0;
            }
            
            QLabel#statsLabel {
                font-size: 16px;
                font-weight: 500;
                color: #34495e;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """

    def _build_ui(self):
        """Constrói a interface do usuário"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Cabeçalho
        header = QHBoxLayout()
        
        title = QLabel("📊 Histórico de Vendas")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        
        # Botão de atualização automática
        self.auto_refresh_btn = QPushButton("Atualização Automática: ON")
        self.auto_refresh_btn.setCheckable(True)
        self.auto_refresh_btn.setChecked(True)
        self.auto_refresh_btn.clicked.connect(self._toggle_auto_refresh)
        header.addWidget(self.auto_refresh_btn)
        
        main_layout.addLayout(header)

        # Estatísticas rápidas
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel("Carregando estatísticas...")
        self.stats_label.setObjectName("statsLabel")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        # Exportar para CSV
        self.btn_csv = QPushButton("Exportar CSV")
        self.btn_csv.clicked.connect(self.exportar_csv)
        stats_layout.addWidget(self.btn_csv)
        
        main_layout.addLayout(stats_layout)

        # Grupo de Filtros
        filter_group = QGroupBox("🔍 Filtros de Busca")
        filter_layout = QFormLayout(filter_group)
        
        # Filtros em linha
        filter_row = QHBoxLayout()
        
        # Filtro por ID
        self.filter_id = QLineEdit()
        self.filter_id.setPlaceholderText("ID da Venda")
        self.filter_id.setMaximumWidth(150)
        filter_row.addWidget(QLabel("ID:"))
        filter_row.addWidget(self.filter_id)
        
        # Filtro por Cliente
        self.filter_cliente = QLineEdit()
        self.filter_cliente.setPlaceholderText("Nome do Cliente")
        self.filter_cliente.setMaximumWidth(200)
        filter_row.addWidget(QLabel("Cliente:"))
        filter_row.addWidget(self.filter_cliente)
        
        # Filtro por Data
        date_filter_layout = QHBoxLayout()
        
        hoje = QDate.currentDate()
        semana_passada = hoje.addDays(-7)
        
        self.filter_data_inicio = QDateEdit(semana_passada)
        self.filter_data_inicio.setCalendarPopup(True)
        self.filter_data_inicio.setDisplayFormat("dd/MM/yyyy")
        date_filter_layout.addWidget(QLabel("De:"))
        date_filter_layout.addWidget(self.filter_data_inicio)
        
        self.filter_data_fim = QDateEdit(hoje)
        self.filter_data_fim.setCalendarPopup(True)
        self.filter_data_fim.setDisplayFormat("dd/MM/yyyy")
        date_filter_layout.addWidget(QLabel("Até:"))
        date_filter_layout.addWidget(self.filter_data_fim)
        
        filter_row.addLayout(date_filter_layout)
        
        # Filtro por Valor
        valor_filter_layout = QHBoxLayout()
        
        self.filter_valor_min = QLineEdit()
        self.filter_valor_min.setPlaceholderText("Mín.")
        self.filter_valor_min.setMaximumWidth(100)
        valor_filter_layout.addWidget(QLabel("Valor:"))
        valor_filter_layout.addWidget(self.filter_valor_min)
        
        valor_filter_layout.addWidget(QLabel("a"))
        
        self.filter_valor_max = QLineEdit()
        self.filter_valor_max.setPlaceholderText("Máx.")
        self.filter_valor_max.setMaximumWidth(100)
        valor_filter_layout.addWidget(self.filter_valor_max)
        
        filter_row.addLayout(valor_filter_layout)
        
        filter_layout.addRow(filter_row)

        # Botões de ação dos filtros
        btn_filter_layout = QHBoxLayout()
        
        self.btn_filter = QPushButton("Aplicar Filtros")
        self.btn_filter.clicked.connect(self.aplicar_filtros)
        
        self.btn_reset = QPushButton("Limpar Filtros")
        self.btn_reset.setObjectName("btnReset")
        self.btn_reset.clicked.connect(self.resetar_filtros)
        
        btn_filter_layout.addWidget(self.btn_filter)
        btn_filter_layout.addWidget(self.btn_reset)
        btn_filter_layout.addStretch()
        
        filter_layout.addRow(btn_filter_layout)
        
        main_layout.addWidget(filter_group)

        # Tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Data/Hora", "Itens", "Total (AOA)"
        ])
        
        # Configurar cabeçalho
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)          # Cliente
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Data
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Itens
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Total
        
        # Configurar seleção
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        main_layout.addWidget(self.table)

        # Barra inferior com ações e total geral
        footer_layout = QHBoxLayout()
        
        # Total geral
        self.total_label = QLabel("Total Geral: AOA 0,00")
        self.total_label.setStyleSheet("font-weight: 600; font-size: 16px; color: #2c3e50;")
        footer_layout.addWidget(self.total_label)
        footer_layout.addStretch()
        
        # Botões de ação
        self.btn_refresh = QPushButton("🔄 Atualizar")
        self.btn_refresh.clicked.connect(self.load_history)
        
        self.btn_detalhes = QPushButton("📄 Ver Detalhes")
        self.btn_detalhes.clicked.connect(self.ver_detalhes)
        
        self.btn_pdf = QPushButton("📊 Gerar PDF")
        self.btn_pdf.setObjectName("btnPdf")
        self.btn_pdf.clicked.connect(self.on_generate_pdf)
        
        footer_layout.addWidget(self.btn_refresh)
        footer_layout.addWidget(self.btn_detalhes)
        footer_layout.addWidget(self.btn_pdf)
        
        main_layout.addLayout(footer_layout)

        # Conectar eventos
        self.table.cellDoubleClicked.connect(self._on_table_activated)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def _toggle_auto_refresh(self, checked: bool):
        """Ativa/desativa atualização automática"""
        if checked:
            self.timer.start(30000)
            self.auto_refresh_btn.setText("Atualização Automática: ON")
            self.auto_refresh_btn.setStyleSheet("background-color: #4CAF50;")
        else:
            self.timer.stop()
            self.auto_refresh_btn.setText("Atualização Automática: OFF")
            self.auto_refresh_btn.setStyleSheet("background-color: #f44336;")

    def _atualizar_automaticamente(self):
        """Atualiza os dados automaticamente"""
        if self.isVisible() and not self.filtro_ativo:
            self.load_history(silencioso=True)

    def load_history(self, silencioso: bool = False):
        """Carrega o histórico de vendas"""
        if not silencioso:
            progress = QProgressDialog("Carregando histórico...", "Cancelar", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            QApplication.processEvents()
        
        try:
            # Coletar filtros
            filtros = {}
            
            if self.filter_id.text():
                try:
                    filtros['venda_id'] = int(self.filter_id.text())
                except ValueError:
                    pass
            
            if self.filter_cliente.text():
                filtros['cliente'] = self.filter_cliente.text()
            
            if self.filter_data_inicio.date() != QDate.currentDate().addDays(-7):
                filtros['data_inicio'] = self.filter_data_inicio.date().toString("yyyy-MM-dd")
            
            if self.filter_data_fim.date() != QDate.currentDate():
                filtros['data_fim'] = self.filter_data_fim.date().toString("yyyy-MM-dd")
            
            # Buscar dados
            self.vendas, self.total_geral = obter_historico(
                venda_id=filtros.get('venda_id'),
                limite=1000,
                data_inicio=filtros.get('data_inicio'),
                data_fim=filtros.get('data_fim'),
                cliente=filtros.get('cliente')
            )
            
            # Atualizar filtro ativo
            self.filtro_ativo = any(filtros.values())
            
            # Atualizar interface
            self._atualizar_tabela()
            self._atualizar_estatisticas()
            
            self.atualizado.emit()
            
        except Exception as e:
            if not silencioso:
                QMessageBox.warning(self, "Erro", f"Erro ao carregar histórico: {str(e)}")
        
        finally:
            if not silencioso:
                progress.close()

    def _atualizar_tabela(self):
        """Atualiza a tabela com os dados carregados"""
        self.table.setRowCount(0)
        
        for venda in self.vendas:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID
            item_id = QTableWidgetItem(str(venda["venda_id"]))
            item_id.setData(Qt.UserRole, venda["venda_id"])
            item_id.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_id)
            
            # Cliente
            cliente = venda["comprador"] or "Cliente não identificado"
            item_cliente = QTableWidgetItem(cliente)
            self.table.setItem(row, 1, item_cliente)
            
            # Data/Hora
            data_obj = datetime.strptime(venda["data"], "%Y-%m-%d %H:%M:%S")
            data_formatada = data_obj.strftime("%d/%m/%Y %H:%M")
            item_data = QTableWidgetItem(data_formatada)
            item_data.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_data)
            
            # Itens
            itens_text = f"{venda['quantidade_total']} itens"
            item_itens = QTableWidgetItem(itens_text)
            item_itens.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, item_itens)
            
            # Total
            total = venda["total"] or 0.0
            item_total = QTableWidgetItem(f"AOA {total:,.2f}")
            item_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Colorir baseado no valor
            if total > 10000:
                item_total.setForeground(QBrush(QColor(0, 100, 0)))  # Verde escuro
            elif total < 1000:
                item_total.setForeground(QBrush(QColor(128, 128, 128)))  # Cinza
            
            self.table.setItem(row, 4, item_total)
        
        # Atualizar label do total geral
        self.total_label.setText(f"Total Geral: AOA {self.total_geral:,.2f}")

    def _atualizar_estatisticas(self):
        """Atualiza as estatísticas exibidas"""
        if not self.vendas:
            self.stats_label.setText("Nenhuma venda encontrada")
            return
        
        total_vendas = len(self.vendas)
        media_valor = self.total_geral / total_vendas if total_vendas > 0 else 0
        
        # Venda mais recente
        mais_recente = max(self.vendas, key=lambda x: x["data"]) if self.vendas else None
        
        stats_text = f"""
        <b>📈 Estatísticas:</b> 
        Total de Vendas: <b>{total_vendas}</b> | 
        Valor Médio: <b>AOA {media_valor:,.2f}</b> | 
        Total Geral: <b>AOA {self.total_geral:,.2f}</b>
        """
        
        if mais_recente:
            stats_text += f" | Última Venda: <b>{mais_recente['data'].split()[0]}</b>"
        
        self.stats_label.setText(stats_text)

    def aplicar_filtros(self):
        """Aplica os filtros selecionados"""
        # Validar valor mínimo/máximo
        valor_min = self.filter_valor_min.text()
        valor_max = self.filter_valor_max.text()
        
        if valor_min:
            try:
                float(valor_min)
            except ValueError:
                QMessageBox.warning(self, "Valor inválido", "Valor mínimo deve ser um número válido.")
                return
        
        if valor_max:
            try:
                float(valor_max)
            except ValueError:
                QMessageBox.warning(self, "Valor inválido", "Valor máximo deve ser um número válido.")
                return
        
        if valor_min and valor_max:
            if float(valor_min) > float(valor_max):
                QMessageBox.warning(self, "Valor inválido", "Valor mínimo não pode ser maior que valor máximo.")
                return
        
        self.load_history()

    def resetar_filtros(self):
        """Reseta todos os filtros"""
        self.filter_id.clear()
        self.filter_cliente.clear()
        
        hoje = QDate.currentDate()
        semana_passada = hoje.addDays(-7)
        
        self.filter_data_inicio.setDate(semana_passada)
        self.filter_data_fim.setDate(hoje)
        
        self.filter_valor_min.clear()
        self.filter_valor_max.clear()
        
        self.filtro_ativo = False
        self.load_history()

    def _on_table_activated(self, row, column):
        """Abre os detalhes da venda ao clicar duas vezes"""
        self.ver_detalhes()

    def _on_selection_changed(self):
        """Atualiza o estado do botão de detalhes"""
        has_selection = self.table.currentRow() >= 0
        self.btn_detalhes.setEnabled(has_selection)

    def ver_detalhes(self):
        """Abre a janela de detalhes da venda selecionada"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Aviso", "Selecione uma venda para ver os detalhes.")
            return
        
        item_id = self.table.item(selected, 0)
        if not item_id:
            return
        
        try:
            venda_id = int(item_id.data(Qt.UserRole))
        except Exception:
            QMessageBox.warning(self, "Erro", "ID da venda inválido.")
            return
        
        # Encontrar a venda nos dados carregados
        venda = None
        for v in self.vendas:
            if v["venda_id"] == venda_id:
                venda = v
                break
        
        if not venda:
            QMessageBox.warning(self, "Erro", "Venda não encontrada.")
            return
        
        dlg = VendaInvoiceDialog(venda, parent=self)
        dlg.exec_()

    def on_generate_pdf(self):
        """Gera PDF da venda selecionada"""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.information(self, "Aviso", "Selecione uma venda para gerar PDF.")
            return
        
        item_id = self.table.item(selected, 0)
        if not item_id:
            QMessageBox.warning(self, "Erro", "Não foi possível obter a venda selecionada.")
            return
        
        try:
            venda_id = int(item_id.data(Qt.UserRole))
        except Exception:
            QMessageBox.warning(self, "Erro", "ID da venda inválido.")
            return
        
        # Encontrar a venda
        venda = None
        for v in self.vendas:
            if v["venda_id"] == venda_id:
                venda = v
                break
        
        if not venda:
            QMessageBox.warning(self, "Erro", "Venda não encontrada.")
            return
        
        # Solicitar local para salvar
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Fatura",
            f"fatura_{venda_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF (*.pdf)"
        )
        
        if not file_name:
            return
        
        try:
            # Gerar PDF usando o diálogo de fatura
            dlg = VendaInvoiceDialog(venda, parent=self)
            dlg.gerar_pdf(file_name, mostrar_mensagem=False)
            QMessageBox.information(self, "Sucesso", f"PDF gerado com sucesso:\n{file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF:\n{str(e)}")

    def exportar_csv(self):
        """Exporta os dados para CSV"""
        if not self.vendas:
            QMessageBox.information(self, "Aviso", "Não há dados para exportar.")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar para CSV",
            f"vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)"
        )
        
        if not file_name:
            return
        
        try:
            with open(file_name, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write("ID;Cliente;Data;Hora;Itens;Total(AOA)\n")
                
                # Dados
                for venda in self.vendas:
                    data_obj = datetime.strptime(venda["data"], "%Y-%m-%d %H:%M:%S")
                    data = data_obj.strftime("%d/%m/%Y")
                    hora = data_obj.strftime("%H:%M")
                    
                    linha = f"""
{venda['venda_id']};
{venda['comprador'] or 'N/A'};
{data};
{hora};
{venda['quantidade_total']};
{venda['total']:.2f}
""".strip()
                    f.write(linha + "\n")
            
            QMessageBox.information(self, "Sucesso", f"Dados exportados com sucesso:\n{file_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar CSV:\n{str(e)}")

    def closeEvent(self, event):
        """Garante que o timer seja parado ao fechar a janela"""
        self.timer.stop()
        super().closeEvent(event)


class VendaInvoiceDialog(QDialog):
    """Diálogo moderno para exibir fatura de venda"""
    
    def __init__(self, venda: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.venda = venda
        self.setWindowTitle(f"Fatura - Venda #{venda.get('venda_id', 'N/A')}")
        self.resize(900, 700)
        self.setStyleSheet(self._get_stylesheet())
        self._build_ui()

    def _get_stylesheet(self) -> str:
        return """
            QDialog {
                background-color: #f5f5f5;
            }
            
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
            }
            
            QTableWidget {
                gridline-color: #e0e0e0;
                selection-background-color: #e3f2fd;
                background-color: white;
            }
            
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: 600;
            }
        """

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Cabeçalho da fatura
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: white;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # Título
        title_layout = QHBoxLayout()
        
        title_label = QLabel("KAMBA FARMA")
        title_label.setStyleSheet("font-size: 28px; font-weight: 700;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        venda_label = QLabel(f"FATURA #{self.venda.get('venda_id', 'N/A')}")
        venda_label.setStyleSheet("font-size: 24px; font-weight: 600;")
        title_layout.addWidget(venda_label)
        
        header_layout.addLayout(title_layout)
        
        # Informações da empresa
        empresa_layout = QHBoxLayout()
        
        empresa_info = QLabel("""
        <b>Kamba Farma Lda.</b><br>
        Av. 21 de Janeiro, Luanda<br>
        Telefone: +244 923 456 789<br>
        Email: info@kambafarma.ao
        """)
        empresa_info.setStyleSheet("font-size: 12px;")
        empresa_layout.addWidget(empresa_info)
        empresa_layout.addStretch()
        
        header_layout.addLayout(empresa_layout)
        
        layout.addWidget(header_frame)

        # Informações da venda
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        info_layout = QHBoxLayout(info_frame)
        
        # Cliente
        cliente_group = QGroupBox("Cliente")
        cliente_layout = QVBoxLayout()
        cliente_label = QLabel(self.venda.get('comprador') or 'Cliente não identificado')
        cliente_label.setStyleSheet("font-size: 16px;")
        cliente_layout.addWidget(cliente_label)
        cliente_group.setLayout(cliente_layout)
        info_layout.addWidget(cliente_group)
        
        # Data
        data_group = QGroupBox("Data da Venda")
        data_layout = QVBoxLayout()
        data_obj = datetime.strptime(self.venda["data"], "%Y-%m-%d %H:%M:%S")
        data_text = data_obj.strftime("%d/%m/%Y %H:%M:%S")
        data_label = QLabel(data_text)
        data_label.setStyleSheet("font-size: 16px;")
        data_layout.addWidget(data_label)
        data_group.setLayout(data_layout)
        info_layout.addWidget(data_group)
        
        # Total
        total_group = QGroupBox("Total")
        total_layout = QVBoxLayout()
        total = self.venda.get('total') or 0.0
        total_label = QLabel(f"AOA {total:,.2f}")
        total_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #2196F3;")
        total_layout.addWidget(total_label)
        data_group.setLayout(total_layout)
        info_layout.addWidget(total_group)
        
        layout.addWidget(info_frame)

        # Tabela de produtos
        produtos_label = QLabel("Itens da Venda")
        produtos_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #2c3e50;")
        layout.addWidget(produtos_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Código", "Produto", "Quantidade", "Preço Unitário", "Subtotal"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        produtos = self.venda.get('produtos') or []
        self.table.setRowCount(len(produtos))
        
        for i, p in enumerate(produtos):
            # Código
            self.table.setItem(i, 0, QTableWidgetItem(str(p.get('produto_id') or 'N/A')))
            
            # Nome do produto
            self.table.setItem(i, 1, QTableWidgetItem(str(p.get('produto_nome') or 'Produto não identificado')))
            
            # Quantidade
            qtd_item = QTableWidgetItem(str(p.get('quantidade') or 0))
            qtd_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, qtd_item)
            
            # Preço unitário
            preco = p.get('preco_unitario') or 0.0
            preco_item = QTableWidgetItem(f"AOA {preco:,.2f}")
            preco_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 3, preco_item)
            
            # Subtotal
            subtotal = p.get('subtotal') or 0.0
            subtotal_item = QTableWidgetItem(f"AOA {subtotal:,.2f}")
            subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            subtotal_item.setForeground(QBrush(QColor(0, 100, 0)))
            self.table.setItem(i, 4, subtotal_item)
        
        layout.addWidget(self.table)

        # Rodapé com totais
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 6px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        footer_layout = QHBoxLayout(footer_frame)
        
        # Estatísticas
        stats_text = f"""
        <b>Resumo da Venda</b><br>
        Total de Itens: <b>{self.venda.get('quantidade_total', 0)}</b><br>
        Quantidade de Produtos: <b>{len(produtos)}</b>
        """
        stats_label = QLabel(stats_text)
        footer_layout.addWidget(stats_label)
        
        footer_layout.addStretch()
        
        # Total
        total_layout = QVBoxLayout()
        total_text = QLabel(f"TOTAL GERAL")
        total_text.setStyleSheet("font-size: 14px; color: #666;")
        total_layout.addWidget(total_text)
        
        total_valor = QLabel(f"AOA {total:,.2f}")
        total_valor.setStyleSheet("font-size: 32px; font-weight: 700; color: #2196F3;")
        total_layout.addWidget(total_valor)
        
        footer_layout.addLayout(total_layout)
        
        layout.addWidget(footer_frame)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_imprimir = QPushButton("🖨️ Imprimir")
        self.btn_imprimir.clicked.connect(self.imprimir)
        
        self.btn_pdf = QPushButton("📄 Salvar PDF")
        self.btn_pdf.clicked.connect(self.gerar_pdf_dialog)
        
        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_imprimir)
        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addWidget(self.btn_fechar)
        
        layout.addLayout(btn_layout)

    def gerar_pdf_dialog(self):
        """Abre diálogo para salvar PDF"""
        venda_id = self.venda.get('venda_id', 'N/A')
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Fatura",
            f"fatura_{venda_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF (*.pdf)"
        )
        
        if file_name:
            self.gerar_pdf(file_name)

    def gerar_pdf(self, file_name: str, mostrar_mensagem: bool = True):
        """Gera PDF da fatura"""
        try:
            venda_id = self.venda.get('venda_id', 'N/A')
            produtos = self.venda.get('produtos') or []
            total = self.venda.get('total') or 0.0
            
            # Criar HTML formatado
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Fatura #{venda_id}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ background: #2196F3; color: white; padding: 20px; border-radius: 8px; }}
                    .company {{ font-size: 28px; font-weight: bold; }}
                    .invoice {{ font-size: 24px; float: right; }}
                    .info {{ margin: 30px 0; }}
                    .section {{ background: white; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th {{ background: #2196F3; color: white; padding: 12px; text-align: left; }}
                    td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                    .total {{ text-align: right; font-size: 24px; color: #2196F3; font-weight: bold; }}
                    .footer {{ margin-top: 40px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="company">KAMBA FARMA</div>
                    <div class="invoice">FATURA #{venda_id}</div>
                    <div style="clear: both;"></div>
                    <div style="font-size: 12px; margin-top: 10px;">
                        Av. 21 de Janeiro, Luanda • Telefone: +244 923 456 789 • Email: info@kambafarma.ao
                    </div>
                </div>
                
                <div class="info section">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <strong>Cliente:</strong><br>
                            {self.venda.get('comprador') or 'Cliente não identificado'}
                        </div>
                        <div>
                            <strong>Data da Venda:</strong><br>
                            {datetime.strptime(self.venda['data'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')}
                        </div>
                    </div>
                </div>
                
                <table>
                    <tr>
                        <th>Código</th>
                        <th>Produto</th>
                        <th style="text-align: center;">Quantidade</th>
                        <th style="text-align: right;">Preço Unitário</th>
                        <th style="text-align: right;">Subtotal</th>
                    </tr>
            """
            
            # Adicionar itens
            for p in produtos:
                html += f"""
                    <tr>
                        <td>{p.get('produto_id') or 'N/A'}</td>
                        <td>{p.get('produto_nome') or 'Produto não identificado'}</td>
                        <td style="text-align: center;">{p.get('quantidade') or 0}</td>
                        <td style="text-align: right;">AOA {p.get('preco_unitario') or 0:,.2f}</td>
                        <td style="text-align: right; color: #006400;">AOA {p.get('subtotal') or 0:,.2f}</td>
                    </tr>
                """
            
            html += f"""
                </table>
                
                <div class="section" style="text-align: right; background: #f8f9fa;">
                    <div style="font-size: 14px; color: #666; margin-bottom: 10px;">
                        Total de Itens: {self.venda.get('quantidade_total', 0)} | 
                        Produtos: {len(produtos)}
                    </div>
                    <div class="total">
                        TOTAL: AOA {total:,.2f}
                    </div>
                </div>
                
                <div class="footer">
                    Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} • Kamba Farma Lda. • Todos os direitos reservados
                </div>
            </body>
            </html>
            """
            
            # Gerar PDF
            doc = QTextDocument()
            doc.setHtml(html)
            
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_name)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
            
            doc.print_(printer)
            
            if mostrar_mensagem:
                QMessageBox.information(self, "Sucesso", f"PDF gerado com sucesso:\n{file_name}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar PDF:\n{str(e)}")

    def imprimir(self):
        """Imprime a fatura"""
        try:
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, self)
            
            if print_dialog.exec_() == QDialog.Accepted:
                # Capturar conteúdo da tabela para impressão
                html = self._gerar_html_impressao()
                
                doc = QTextDocument()
                doc.setHtml(html)
                doc.print_(printer)
                
                QMessageBox.information(self, "Sucesso", "Documento enviado para impressão.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao imprimir:\n{str(e)}")

    def _gerar_html_impressao(self) -> str:
        """Gera HTML para impressão"""
        venda_id = self.venda.get('venda_id', 'N/A')
        produtos = self.venda.get('produtos') or []
        total = self.venda.get('total') or 0.0
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: #2196F3; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
                .total {{ font-size: 18px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Kamba Farma - Fatura #{venda_id}</h1>
            <p><strong>Cliente:</strong> {self.venda.get('comprador') or 'N/A'}</p>
            <p><strong>Data:</strong> {self.venda['data']}</p>
            
            <table>
                <tr>
                    <th>Produto</th>
                    <th>Qtd</th>
                    <th>Preço Unit.</th>
                    <th>Subtotal</th>
                </tr>
        """
        
        for p in produtos:
            html += f"""
                <tr>
                    <td>{p.get('produto_nome') or 'N/A'}</td>
                    <td>{p.get('quantidade') or 0}</td>
                    <td>AOA {p.get('preco_unitario') or 0:,.2f}</td>
                    <td>AOA {p.get('subtotal') or 0:,.2f}</td>
                </tr>
            """
        
        html += f"""
            </table>
            <p class="total">Total: AOA {total:,.2f}</p>
        </body>
        </html>
        """
        
        return html


# =========================================================
# Execução direta
# =========================================================
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    
    # Definir ícone da aplicação (se disponível)
    try:
        if os.path.exists("icon.png"):
            app.setWindowIcon(QIcon("icon.png"))
    except:
        pass
    
    win = HistoricoVendaView()
    win.show()
    sys.exit(app.exec_())


__all__ = ["obter_historico", "HistoricoVendaView", "VendaInvoiceDialog"]