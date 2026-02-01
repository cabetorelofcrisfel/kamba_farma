"""
Módulo simplificado de venda de produtos - Apenas lógica de venda
Sem botões, sem UI complexa
"""

from pathlib import Path
import sys
import sqlite3
import json
from datetime import datetime

# Configurar caminhos
src_root = Path(__file__).resolve().parent.parent.parent
project_root = src_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))


class VendorSimples:
    """Classe para gerenciar vendas de produtos"""
    
    def __init__(self, db_path=None):
        """
        Inicializa o vendedor
        
        Args:
            db_path: Caminho para o banco de dados (opcional)
        """
        if db_path is None:
            # Encontrar o banco de dados automaticamente
            _ROOT = Path(__file__).resolve()
            for _ in range(8):
                if (_ROOT / 'database').exists():
                    self.db_path = _ROOT / 'database' / 'kamba_farma.db'
                    break
                _ROOT = _ROOT.parent
            else:
                self.db_path = project_root / 'database' / 'kamba_farma.db'
        else:
            self.db_path = Path(db_path)
        
        self.cart_items = []  # Itens no carrinho
    
    def buscar_produto(self, termo_busca):
        """
        Busca um produto no banco de dados
        
        Args:
            termo_busca: Nome, código ou categoria do produto
            
        Returns:
            Dicionário com dados do produto ou None
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar por nome, código ou categoria
            query = """
                SELECT id, nome, preco, estoque, codigo, categoria, imagem
                FROM produtos
                WHERE nome LIKE ? OR codigo LIKE ? OR categoria LIKE ?
                LIMIT 1
            """
            
            termo = f"%{termo_busca}%"
            cursor.execute(query, (termo, termo, termo))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return {
                    'id': resultado['id'],
                    'nome': resultado['nome'],
                    'preco': resultado['preco'],
                    'estoque': resultado['estoque'],
                    'codigo': resultado['codigo'],
                    'categoria': resultado['categoria'],
                    'imagem': resultado['imagem']
                }
            return None
            
        except Exception as e:
            print(f"Erro ao buscar produto: {e}")
            return None
    
    def adicionar_ao_carrinho(self, produto_id, nome, quantidade, preco):
        """
        Adiciona um item ao carrinho
        
        Args:
            produto_id: ID do produto
            nome: Nome do produto
            quantidade: Quantidade a vender
            preco: Preço unitário
            
        Returns:
            True se adicionado, False se já existe
        """
        # Verificar se já existe
        for item in self.cart_items:
            if item['produto_id'] == produto_id:
                item['quantidade'] += quantidade
                return False
        
        # Adicionar novo item
        self.cart_items.append({
            'produto_id': produto_id,
            'nome': nome,
            'quantidade': quantidade,
            'preco': preco,
            'subtotal': quantidade * preco
        })
        return True
    
    def remover_do_carrinho(self, produto_id):
        """
        Remove um item do carrinho
        
        Args:
            produto_id: ID do produto
        """
        self.cart_items = [item for item in self.cart_items if item['produto_id'] != produto_id]
    
    def atualizar_quantidade(self, produto_id, nova_quantidade):
        """
        Atualiza a quantidade de um item no carrinho
        
        Args:
            produto_id: ID do produto
            nova_quantidade: Nova quantidade
        """
        for item in self.cart_items:
            if item['produto_id'] == produto_id:
                item['quantidade'] = nova_quantidade
                item['subtotal'] = nova_quantidade * item['preco']
                break
    
    def obter_total(self):
        """Retorna o total da venda"""
        return sum(item['subtotal'] for item in self.cart_items)
    
    def obter_quantidade_itens(self):
        """Retorna a quantidade total de itens"""
        return len(self.cart_items)
    
    def obter_carrinho(self):
        """Retorna o carrinho atual"""
        return self.cart_items.copy()
    
    def limpar_carrinho(self):
        """Limpa o carrinho"""
        self.cart_items = []
    
    def finalizar_venda(self, cliente_nome):
        """
        Finaliza a venda e registra no banco de dados
        
        Args:
            cliente_nome: Nome do cliente
            
        Returns:
            ID da venda ou None se falhar
        """
        if not self.cart_items:
            print("Erro: Carrinho vazio!")
            return None
        
        if not cliente_nome or not cliente_nome.strip():
            print("Erro: Nome do cliente obrigatório!")
            return None
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            total = self.obter_total()
            data_venda = datetime.now().isoformat()
            
            # Inserir venda
            cursor.execute("""
                INSERT INTO vendas (cliente, total, data_venda, status)
                VALUES (?, ?, ?, ?)
            """, (cliente_nome, total, data_venda, 'completa'))
            
            venda_id = cursor.lastrowid
            
            # Inserir itens da venda
            for item in self.cart_items:
                cursor.execute("""
                    INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    venda_id,
                    item['produto_id'],
                    item['quantidade'],
                    item['preco'],
                    item['subtotal']
                ))
                
                # Atualizar estoque
                cursor.execute("""
                    UPDATE produtos
                    SET estoque = estoque - ?
                    WHERE id = ?
                """, (item['quantidade'], item['produto_id']))
            
            conn.commit()
            conn.close()
            
            # Limpar carrinho após sucesso
            self.limpar_carrinho()
            
            return venda_id
            
        except Exception as e:
            print(f"Erro ao finalizar venda: {e}")
            return None


# Função auxiliar para vender um produto
def vender_produto(produto_termo, quantidade, cliente_nome, db_path=None):
    """
    Função simples para vender um produto
    
    Args:
        produto_termo: Nome, código ou categoria do produto
        quantidade: Quantidade a vender
        cliente_nome: Nome do cliente
        db_path: Caminho do banco de dados (opcional)
        
    Returns:
        Dicionário com resultado da venda
    """
    vendor = VendorSimples(db_path)
    
    # Buscar produto
    produto = vendor.buscar_produto(produto_termo)
    if not produto:
        return {'sucesso': False, 'mensagem': 'Produto não encontrado'}
    
    # Validar estoque
    if produto['estoque'] < quantidade:
        return {'sucesso': False, 'mensagem': f'Estoque insuficiente. Disponível: {produto["estoque"]}'}
    
    # Adicionar ao carrinho
    vendor.adicionar_ao_carrinho(
        produto['id'],
        produto['nome'],
        quantidade,
        produto['preco']
    )
    
    # Finalizar venda
    venda_id = vendor.finalizar_venda(cliente_nome)
    
    if venda_id:
        return {
            'sucesso': True,
            'venda_id': venda_id,
            'mensagem': f'Venda finalizada com sucesso (ID: {venda_id})',
            'produto': produto['nome'],
            'quantidade': quantidade,
            'total': vendor.obter_total()
        }
    else:
        return {'sucesso': False, 'mensagem': 'Erro ao registrar venda'}


if __name__ == '__main__':
    # Exemplo de uso
    print("=== Sistema Simplificado de Venda ===\n")
    
    # Criar instância
    vendor = VendorSimples()
    
    # Exemplo 1: Buscar produto
    print("1. Buscando produto 'Paracetamol'...")
    produto = vendor.buscar_produto('Paracetamol')
    if produto:
        print(f"   Produto encontrado: {produto['nome']}")
        print(f"   Preço: AOA {produto['preco']:.2f}")
        print(f"   Estoque: {produto['estoque']}")
    else:
        print("   Produto não encontrado")
    
    print("\n2. Adicionando ao carrinho...")
    if produto:
        vendor.adicionar_ao_carrinho(produto['id'], produto['nome'], 2, produto['preco'])
        print(f"   Adicionado 2x {produto['nome']}")
    
    print(f"\n3. Total no carrinho: AOA {vendor.obter_total():.2f}")
    print(f"   Itens: {vendor.obter_quantidade_itens()}")
    
    print("\n4. Finalizando venda para cliente 'João Silva'...")
    resultado = vender_produto('Paracetamol', 1, 'João Silva')
    print(f"   Resultado: {resultado}")
