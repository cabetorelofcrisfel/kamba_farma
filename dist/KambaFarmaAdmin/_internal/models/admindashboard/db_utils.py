"""
Utilitários para gerenciar a tabela transacoes_financeiras.
"""

from pathlib import Path
import sqlite3


def _find_db_file():
    """Procura pelo arquivo de banco de dados na hierarquia de diretórios."""
    root = Path(__file__).resolve()
    for _ in range(8):
        db_dir = root / "database"
        if db_dir.exists():
            db_file = db_dir / "kamba_farma.db"
            return db_file if db_file.exists() else None
        root = root.parent
    return None


def ensure_transacoes_table(db_file):
    """
    Garante que a tabela transacoes_financeiras existe com a estrutura correta.
    
    Colunas:
    - id: PRIMARY KEY AUTOINCREMENT
    - tipo: TEXT NOT NULL (kumbu, emprestimo, saida)
    - descricao: TEXT (descrição customizada)
    - valor: REAL NOT NULL
    - data_transacao: TEXT (yyyy-MM-dd)
    - criado_em: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    if not db_file:
        return False
    
    try:
        conn = sqlite3.connect(str(db_file))
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transacoes_financeiras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                descricao TEXT,
                valor REAL NOT NULL,
                data_transacao TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao criar tabela transacoes_financeiras: {e}")
        return False
