"""Módulo para tratar devoluções de produtos no painel de administração.

Fornece helpers para registrar devoluções e validar entradas.
"""

from typing import Dict, Any
import sqlite3
from pathlib import Path
import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt


def registrar_devolucao(venda_id: int, produto_id: int, quantidade: int, motivo: str) -> Dict[str, Any]:
    """Registra a devolução de um produto associado a uma venda.

    Args:
        venda_id: ID da venda original.
        produto_id: ID do produto devolvido.
        quantidade: Quantidade devolvida.
        motivo: Texto explicando o motivo da devolução.

    Returns:
        Um dicionário com o resultado da operação.
    """
    # localizar arquivo de banco: subir até encontrar a pasta `database`
    file_path = Path(__file__).resolve()
    _ROOT = file_path
    for _ in range(8):
        if (_ROOT / 'database').exists():
            break
        _ROOT = _ROOT.parent
    db_file = _ROOT / 'database' / 'kamba_farma.db'

    if not db_file.exists():
        raise DevolucaoError(f"Arquivo de banco de dados não encontrado: {db_file}")

    try:
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # verificar existência do histórico e tempo da compra
        cur.execute("SELECT quantidade_total, tempo_compra FROM historico_compra WHERE id = ?", (venda_id,))
        hc = cur.fetchone()
        if not hc:
            raise DevolucaoError(f"Histórico de compra {venda_id} não encontrado")

        # checar prazo de devolução: máximo 4 horas desde tempo_compra
        tempo_compra = hc['tempo_compra']
        if tempo_compra:
            tstr = str(tempo_compra)
            if '.' in tstr:
                tstr = tstr.split('.')[0]
            try:
                comprado_em = datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
            except Exception:
                try:
                    comprado_em = datetime.datetime.fromisoformat(tstr)
                except Exception:
                    comprado_em = None

            if comprado_em is not None:
                delta = datetime.datetime.now() - comprado_em
                if delta.total_seconds() > 4 * 3600:
                    raise DevolucaoError("Prazo máximo de devolução (4 horas) excedido.")

        # verificar item no histórico
        cur.execute(
            "SELECT id, quantidade FROM historico_compra_itens WHERE historico_compra_id = ? AND produto_id = ?",
            (venda_id, produto_id)
        )
        item = cur.fetchone()
        if not item:
            raise DevolucaoError("Produto não encontrado no histórico informado")

        atual_qtd = item['quantidade'] or 0
        if quantidade > atual_qtd:
            raise DevolucaoError(f"Quantidade a devolver ({quantidade}) maior que a registrada ({atual_qtd})")

        novo_valor = atual_qtd - quantidade

        # iniciar transação
        conn.execute('BEGIN')

        # atualizar stock do produto (estornar)
        cur.execute("UPDATE produtos SET stock = COALESCE(stock,0) + ? WHERE id = ?", (quantidade, produto_id))

        if novo_valor > 0:
            cur.execute(
                "UPDATE historico_compra_itens SET quantidade = ? WHERE id = ?",
                (novo_valor, item['id'])
            )
        else:
            cur.execute(
                "DELETE FROM historico_compra_itens WHERE id = ?",
                (item['id'],)
            )

        # diminuir quantidade_total, garantindo não ficar negativo
        quantidade_total = hc['quantidade_total'] or 0
        nova_total = max(0, quantidade_total - quantidade)
        cur.execute(
            "UPDATE historico_compra SET quantidade_total = ? WHERE id = ?",
            (nova_total, venda_id)
        )

        # opcional: registrar log da devolução
        cur.execute(
            "INSERT INTO logs_sistema (usuario_id, acao, tabela_afetada, registro_id) VALUES (?, ?, ?, ?)",
            (None, f"devolucao: produto {produto_id} quantidade {quantidade}", 'historico_compra', venda_id)
        )

        conn.commit()
        return {
            "status": "ok",
            "historico_compra_id": venda_id,
            "produto_id": produto_id,
            "devolvido": quantidade,
            "restante_no_historico": novo_valor,
            "quantidade_total": nova_total,
        }
    except DevolucaoError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise DevolucaoError(str(e))
    finally:
        try:
            conn.close()
        except Exception:
            pass


class DevolucaoError(Exception):
    """Exceção para erros durante a devolução de produtos."""


class DevolucaoDeProdutoView(QWidget):
    """View simples para procurar por cliente e devolver produtos comprados.

    Pesquisa por `comprador_nome` na tabela `historico_compra` e exibe
    os itens associados em `historico_compra_itens`. Permite devolver
    uma quantidade, que atualiza o `stock` em `produtos` e chama o
    helper `registrar_devolucao`.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

        # localizar arquivo de banco: subir até encontrar a pasta `database`
        file_path = Path(__file__).resolve()
        _ROOT = file_path
        for _ in range(8):
            if (_ROOT / 'database').exists():
                break
            _ROOT = _ROOT.parent
        self._db_file = _ROOT / 'database' / 'kamba_farma.db'

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("🔎 Nome do Cliente:"))
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Digite o nome do cliente...")
        top.addWidget(self.client_input, 1)
        self.search_btn = QPushButton("Pesquisar")
        top.addWidget(self.search_btn)
        layout.addLayout(top)

        # tabela de resultados
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Histórico ID", "Produto", "Quantidade", "Total (Compra)", "Tempo", "Ações"])
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        # conexões
        self.search_btn.clicked.connect(self.search_by_client)
        self.client_input.returnPressed.connect(self.search_by_client)

    def search_by_client(self):
        term = self.client_input.text().strip()
        if not term:
            QMessageBox.warning(self, "Aviso", "Digite o nome do cliente para pesquisar.")
            return

        if not self._db_file.exists():
            QMessageBox.critical(self, "Erro", f"Arquivo de banco de dados não encontrado: {self._db_file}")
            return

        try:
            conn = sqlite3.connect(str(self._db_file))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            like = f"%{term}%"
            cur.execute(
                """
                SELECT hc.id AS historico_id, hci.produto_id, p.nome_comercial AS produto,
                       hci.quantidade, hc.quantidade_total, hc.tempo_compra
                FROM historico_compra hc
                JOIN historico_compra_itens hci ON hc.id = hci.historico_compra_id
                LEFT JOIN produtos p ON p.id = hci.produto_id
                WHERE hc.comprador_nome LIKE ?
                ORDER BY hc.tempo_compra DESC
                """,
                (like,)
            )
            rows = cur.fetchall()
            conn.close()

            self.table.setRowCount(0)
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r['historico_id'])))
                self.table.setItem(row, 1, QTableWidgetItem(r['produto'] or '---'))
                self.table.setItem(row, 2, QTableWidgetItem(str(r['quantidade'])))
                self.table.setItem(row, 3, QTableWidgetItem(str(r['quantidade_total'] or '0')))
                self.table.setItem(row, 4, QTableWidgetItem(str(r['tempo_compra'])))

                btn = QPushButton('Devolver')
                btn.clicked.connect(lambda _, hid=r['historico_id'], pid=r['produto_id'], q=r['quantidade']: self._handle_devolucao(hid, pid, q))
                self.table.setCellWidget(row, 5, btn)

            if not rows:
                QMessageBox.information(self, "Nenhum resultado", "Nenhum registro de compra encontrado para esse cliente.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar histórico: {e}")

    def _handle_devolucao(self, historico_id: int, produto_id: int, max_qtd: int):
        # pedir quantidade a devolver
        qtd, ok = QInputDialog.getInt(self, "Quantidade a devolver", "Quantidade:", 1, 1, max_qtd)
        if not ok:
            return

        motivo, ok2 = QInputDialog.getText(self, "Motivo da Devolução", "Motivo:")
        if not ok2:
            return

        # atualizar stock do produto e registrar devolução via helper
        try:
            # registrar_devolucao fará validações e atualizará o stock no mesmo banco
            registrar_devolucao(historico_id, produto_id, qtd, motivo)

            QMessageBox.information(self, "Devolução", "Devolução registrada com sucesso e stock atualizado.")
            # atualizar tabela visual (simples: re-executar pesquisa)
            self.search_by_client()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar devolução: {e}")


__all__ = ["registrar_devolucao", "DevolucaoError", "DevolucaoDeProdutoView"]
