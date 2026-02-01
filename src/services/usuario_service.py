import sqlite3
from typing import Optional

from core.auth import hash_password
from config.settings import DB_FILE


def criar_usuario(username, password_hash, role='user'):
    return {'username': username, 'role': role}


def authenticate(username: str, password: str) -> Optional[dict]:
    """Autentica um utilizador contra a base de dados.

    Retorna um dicionário com `username` e `role` se credenciais válidas,
    caso contrário `None`.
    """
    pw_hash = hash_password(password)
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute('SELECT username, role FROM usuarios WHERE username = ? AND password_hash = ?',
                    (username, pw_hash))
        row = cur.fetchone()
        if row:
            return {'username': row['username'], 'role': row['role']}
        return None
    finally:
        conn.close()
