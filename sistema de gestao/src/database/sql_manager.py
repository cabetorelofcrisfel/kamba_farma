import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple


class SQLDatabaseManager:
    """Gerenciador de banco de dados SQL (SQLite)"""
    
    def __init__(self, db_path: str = None):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                '../../assets/databases/default.db'
            )
        
        self.db_path = db_path
        self._ensure_dir_exists()
    
    def _ensure_dir_exists(self):
        """Cria diretório se não existir"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        """Cria conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Executa uma consulta SELECT
        
        Args:
            query: Query SQL
            params: Parâmetros da query
            
        Returns:
            Lista de dicionários com resultados
        """
        try:
            conn = self.connect()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except sqlite3.Error as e:
            raise Exception(f"Erro ao executar query: {str(e)}")
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Executa INSERT, UPDATE ou DELETE
        
        Args:
            query: Query SQL
            params: Parâmetros da query
            
        Returns:
            Número de linhas afetadas
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return affected_rows
        except sqlite3.Error as e:
            raise Exception(f"Erro ao executar update: {str(e)}")
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Cria uma tabela
        
        Args:
            table_name: Nome da tabela
            columns: Dicionário {nome_coluna: tipo_dados}
                    Ex: {'id': 'INTEGER PRIMARY KEY', 'nome': 'TEXT NOT NULL'}
            
        Returns:
            True se criado com sucesso
        """
        try:
            column_defs = ', '.join([f'{col} {type_def}' for col, type_def in columns.items()])
            query = f'CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})'
            
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao criar tabela: {str(e)}")
    
    def drop_table(self, table_name: str) -> bool:
        """
        Deleta uma tabela
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            True se deletado com sucesso
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Erro ao deletar tabela: {str(e)}")
    
    def get_tables(self) -> List[str]:
        """
        Retorna lista de todas as tabelas
        
        Returns:
            Lista com nomes das tabelas
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except sqlite3.Error as e:
            raise Exception(f"Erro ao listar tabelas: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """
        Retorna schema de uma tabela
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Lista de dicionários com informações das colunas
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'dflt_value': row[4],
                    'pk': row[5]
                })
            
            conn.close()
            return columns
        except sqlite3.Error as e:
            raise Exception(f"Erro ao obter schema: {str(e)}")
    
    def insert_row(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Insere uma linha na tabela
        
        Args:
            table_name: Nome da tabela
            data: Dicionário {coluna: valor}
            
        Returns:
            ID da linha inserida
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())
            
            query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
            return self.execute_update(query, values)
        except Exception as e:
            raise Exception(f"Erro ao inserir linha: {str(e)}")
    
    def update_row(self, table_name: str, data: Dict[str, Any], where: str = None, 
                   where_params: tuple = ()) -> int:
        """
        Atualiza uma ou mais linhas
        
        Args:
            table_name: Nome da tabela
            data: Dicionário {coluna: valor} com dados a atualizar
            where: Cláusula WHERE (ex: 'id = ?')
            where_params: Parâmetros para WHERE
            
        Returns:
            Número de linhas afetadas
        """
        try:
            set_clause = ', '.join([f'{col} = ?' for col in data.keys()])
            values = tuple(data.values()) + where_params
            
            query = f'UPDATE {table_name} SET {set_clause}'
            if where:
                query += f' WHERE {where}'
            
            return self.execute_update(query, values)
        except Exception as e:
            raise Exception(f"Erro ao atualizar linha: {str(e)}")
    
    def delete_row(self, table_name: str, where: str = None, 
                   where_params: tuple = ()) -> int:
        """
        Deleta uma ou mais linhas
        
        Args:
            table_name: Nome da tabela
            where: Cláusula WHERE (ex: 'id = ?')
            where_params: Parâmetros para WHERE
            
        Returns:
            Número de linhas deletadas
        """
        try:
            query = f'DELETE FROM {table_name}'
            if where:
                query += f' WHERE {where}'
            
            return self.execute_update(query, where_params)
        except Exception as e:
            raise Exception(f"Erro ao deletar linha: {str(e)}")
    
    def get_row_count(self, table_name: str) -> int:
        """
        Retorna número de linhas em uma tabela
        
        Args:
            table_name: Nome da tabela
            
        Returns:
            Número de linhas
        """
        try:
            results = self.execute_query(f'SELECT COUNT(*) as count FROM {table_name}')
            return results[0]['count'] if results else 0
        except Exception as e:
            raise Exception(f"Erro ao contar linhas: {str(e)}")
    
    def export_to_sql(self, output_path: str) -> bool:
        """
        Exporta banco de dados para arquivo SQL
        
        Args:
            output_path: Caminho do arquivo de saída
            
        Returns:
            True se exportado com sucesso
        """
        try:
            conn = self.connect()
            with open(output_path, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            conn.close()
            return True
        except Exception as e:
            raise Exception(f"Erro ao exportar banco: {str(e)}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o banco de dados
        
        Returns:
            Dicionário com informações do banco
        """
        try:
            tables = self.get_tables()
            total_rows = sum([self.get_row_count(table) for table in tables])
            
            return {
                'path': self.db_path,
                'exists': os.path.exists(self.db_path),
                'size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
                'tables_count': len(tables),
                'tables': tables,
                'total_rows': total_rows
            }
        except Exception as e:
            raise Exception(f"Erro ao obter informações: {str(e)}")
