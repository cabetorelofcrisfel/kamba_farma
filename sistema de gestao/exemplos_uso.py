#!/usr/bin/env python3
"""
Exemplos de uso do SQLDatabaseManager
Demonstra como usar programaticamente o gerenciador de banco de dados
"""

import os
from src.database.sql_manager import SQLDatabaseManager


def exemplo_criar_banco():
    """Exemplo 1: Criar novo banco de dados"""
    print("=== Exemplo 1: Criar Novo Banco ===\n")
    
    db_path = os.path.join(
        os.path.dirname(__file__),
        'assets/databases/exemplo.db'
    )
    
    db = SQLDatabaseManager(db_path)
    print(f"✓ Banco criado: {db_path}")
    
    return db


def exemplo_criar_tabelas(db):
    """Exemplo 2: Criar tabelas"""
    print("\n=== Exemplo 2: Criar Tabelas ===\n")
    
    # Tabela de clientes
    clientes_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'nome': 'TEXT NOT NULL',
        'email': 'TEXT UNIQUE NOT NULL',
        'telefone': 'TEXT',
        'data_cadastro': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
    }
    
    db.create_table('clientes', clientes_columns)
    print("✓ Tabela 'clientes' criada")
    
    # Tabela de produtos
    produtos_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'nome': 'TEXT NOT NULL',
        'preco': 'REAL NOT NULL',
        'estoque': 'INTEGER DEFAULT 0',
        'descricao': 'TEXT'
    }
    
    db.create_table('produtos', produtos_columns)
    print("✓ Tabela 'produtos' criada")
    
    # Tabela de vendas
    vendas_columns = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'cliente_id': 'INTEGER NOT NULL',
        'produto_id': 'INTEGER NOT NULL',
        'quantidade': 'INTEGER NOT NULL',
        'valor_total': 'REAL NOT NULL',
        'data_venda': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
        'FOREIGN KEY(cliente_id)': 'REFERENCES clientes(id)',
        'FOREIGN KEY(produto_id)': 'REFERENCES produtos(id)'
    }
    
    db.create_table('vendas', vendas_columns)
    print("✓ Tabela 'vendas' criada")


def exemplo_inserir_dados(db):
    """Exemplo 3: Inserir dados"""
    print("\n=== Exemplo 3: Inserir Dados ===\n")
    
    # Inserir clientes
    clientes = [
        {'nome': 'João Silva', 'email': 'joao@email.com', 'telefone': '11999999999'},
        {'nome': 'Maria Santos', 'email': 'maria@email.com', 'telefone': '11888888888'},
        {'nome': 'Pedro Oliveira', 'email': 'pedro@email.com', 'telefone': '11777777777'}
    ]
    
    for cliente in clientes:
        db.insert_row('clientes', cliente)
        print(f"✓ Cliente inserido: {cliente['nome']}")
    
    # Inserir produtos
    produtos = [
        {'nome': 'Dipirona 500mg', 'preco': 5.50, 'estoque': 100, 'descricao': 'Analgésico'},
        {'nome': 'Amoxicilina 500mg', 'preco': 12.00, 'estoque': 50, 'descricao': 'Antibiótico'},
        {'nome': 'Vitamina C 1000mg', 'preco': 15.00, 'estoque': 75, 'descricao': 'Suplemento'}
    ]
    
    for produto in produtos:
        db.insert_row('produtos', produto)
        print(f"✓ Produto inserido: {produto['nome']}")


def exemplo_consultar_dados(db):
    """Exemplo 4: Consultar dados"""
    print("\n=== Exemplo 4: Consultar Dados ===\n")
    
    # Listar clientes
    print("Clientes cadastrados:")
    clientes = db.execute_query('SELECT * FROM clientes')
    for cliente in clientes:
        print(f"  - {cliente['nome']} ({cliente['email']})")
    
    # Listar produtos
    print("\nProdutos cadastrados:")
    produtos = db.execute_query('SELECT * FROM produtos')
    for produto in produtos:
        print(f"  - {produto['nome']}: R$ {produto['preco']:.2f}")
    
    # Consulta com filtro
    print("\nProdutos com preço > R$ 10:")
    caros = db.execute_query('SELECT * FROM produtos WHERE preco > ?', (10.0,))
    for produto in caros:
        print(f"  - {produto['nome']}: R$ {produto['preco']:.2f}")


def exemplo_atualizar_dados(db):
    """Exemplo 5: Atualizar dados"""
    print("\n=== Exemplo 5: Atualizar Dados ===\n")
    
    # Atualizar estoque de um produto
    db.update_row(
        'produtos',
        {'estoque': 120},
        'nome = ?',
        ('Dipirona 500mg',)
    )
    print("✓ Estoque de Dipirona atualizado para 120")
    
    # Verificar atualização
    produto = db.execute_query(
        'SELECT * FROM produtos WHERE nome = ?',
        ('Dipirona 500mg',)
    )[0]
    print(f"  Novo estoque: {produto['estoque']}")


def exemplo_deletar_dados(db):
    """Exemplo 6: Deletar dados"""
    print("\n=== Exemplo 6: Deletar Dados ===\n")
    
    # Deletar cliente (se não houver vendas)
    db.delete_row('clientes', 'nome = ?', ('Pedro Oliveira',))
    print("✓ Cliente 'Pedro Oliveira' deletado")
    
    # Listar clientes restantes
    clientes = db.execute_query('SELECT COUNT(*) as total FROM clientes')
    print(f"  Total de clientes: {clientes[0]['total']}")


def exemplo_informacoes_banco(db):
    """Exemplo 7: Obter informações do banco"""
    print("\n=== Exemplo 7: Informações do Banco ===\n")
    
    info = db.get_database_info()
    
    print(f"Caminho: {info['path']}")
    print(f"Existe: {info['exists']}")
    print(f"Tamanho: {info['size'] / 1024:.2f} KB")
    print(f"Número de tabelas: {info['tables_count']}")
    print(f"Tabelas: {', '.join(info['tables'])}")
    print(f"Total de linhas: {info['total_rows']}")


def exemplo_exportar_banco(db):
    """Exemplo 8: Exportar banco para SQL"""
    print("\n=== Exemplo 8: Exportar Banco ===\n")
    
    output_file = os.path.join(
        os.path.dirname(__file__),
        'assets/databases/exemplo_export.sql'
    )
    
    db.export_to_sql(output_file)
    print(f"✓ Banco exportado para: {output_file}")
    
    # Mostrar conteúdo do arquivo
    with open(output_file, 'r') as f:
        content = f.read()
        print(f"\nPrimeiras 500 caracteres do arquivo SQL:")
        print(content[:500] + "...")


def main():
    """Executa todos os exemplos"""
    print("\n" + "="*60)
    print("EXEMPLOS DE USO - SQLDatabaseManager")
    print("="*60 + "\n")
    
    try:
        # Exemplo 1: Criar banco
        db = exemplo_criar_banco()
        
        # Exemplo 2: Criar tabelas
        exemplo_criar_tabelas(db)
        
        # Exemplo 3: Inserir dados
        exemplo_inserir_dados(db)
        
        # Exemplo 4: Consultar dados
        exemplo_consultar_dados(db)
        
        # Exemplo 5: Atualizar dados
        exemplo_atualizar_dados(db)
        
        # Exemplo 6: Deletar dados
        exemplo_deletar_dados(db)
        
        # Exemplo 7: Informações
        exemplo_informacoes_banco(db)
        
        # Exemplo 8: Exportar
        exemplo_exportar_banco(db)
        
        print("\n" + "="*60)
        print("✓ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERRO: {str(e)}\n")


if __name__ == '__main__':
    main()
