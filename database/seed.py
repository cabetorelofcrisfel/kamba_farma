from pathlib import Path
from .db import connect, get_db_path
import sqlite3
import hashlib


def seed(db_path: Path):
    conn = connect(db_path)
    cur = conn.cursor()
    # criar admin se não existir (tabela `usuarios` - legado)
    try:
        cur.execute("INSERT INTO usuarios (nome, senha_hash, perfil) VALUES (?, ?, ?) ",
                    ("Administrador", hashlib.sha256(b"admin123").hexdigest(), "admin"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

    # criar um registro em user_admin se não existir
    try:
        senha = "admin123"
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        cur.execute(
            "INSERT INTO user_admin (nome, contacto, numero_bi, ft, senha_hash, localizacao, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("Administrador", "+244000000000", "000000000", None, senha_hash, "Sede", "admin@kamba.local")
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass


if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1]
    dbp = get_db_path(base)
    seed(dbp)
