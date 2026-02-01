from pathlib import Path
import argparse
import os
import sqlite3
import time
from database.db import connect, get_db_path


def human_readable(bytes_size):
    for unit in ['B','KB','MB','GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f}TB"


def ensure_tables(conn: sqlite3.Connection):
    # assume schema already created; simple check
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos'")
    if not cur.fetchone():
        raise RuntimeError('Table `produtos` not found in database. Run schema first.')


def insert_product(conn, name, blob_bytes):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO produtos (nome_comercial, principio_ativo, foto, categoria, forma_farmaceutica,
            preco_venda, preco_compra, stock, codigo_barras, unidade, stock_minimo, ativo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, 'ativo-'+name, sqlite3.Binary(blob_bytes), 'GERAL', 'COMPRIMIDO',
         0.0, 0.0, 0, None, 'un', 0, 1)
    )


def main():
    parser = argparse.ArgumentParser(description='Bulk insert products until DB reaches target size (MB)')
    parser.add_argument('--db', help='Path to DB file (optional)')
    parser.add_argument('--target-mb', type=int, default=10, help='Target DB size in MB (default 10)')
    parser.add_argument('--per-row-kb', type=int, default=50, help='Approx bytes per product blob in KB (default 50)')
    parser.add_argument('--commit-every', type=int, default=100, help='Commit every N inserts')
    args = parser.parse_args()

    base = Path(__file__).resolve().parents[1]
    db_path = Path(args.db) if args.db else get_db_path(base)

    if not db_path.exists():
        print(f'Database not found at {db_path}.')
        return

    conn = connect(db_path)
    ensure_tables(conn)

    target_bytes = args.target_mb * 1024 * 1024
    per_row = max(1, args.per_row_kb) * 1024

    print(f'Starting bulk insert into DB: {db_path} target {args.target_mb}MB per-row {args.per_row_kb}KB')

    def db_size():
        try:
            return db_path.stat().st_size
        except Exception:
            return 0

    inserted = 0
    start_size = db_size()
    print('Current DB size:', human_readable(start_size))

    try:
        while db_size() < target_bytes:
            remaining = target_bytes - db_size()
            # adjust last blob size to not overshoot too much
            blob_size = per_row if remaining > per_row else remaining
            if blob_size <= 0:
                break
            name = f'Produto_bulk_{int(time.time()*1000)}_{inserted}'
            blob = os.urandom(int(blob_size))
            insert_product(conn, name, blob)
            inserted += 1
            if inserted % args.commit_every == 0:
                conn.commit()
            if inserted % 50 == 0:
                print(f'Inserted {inserted} rows, DB size {human_readable(db_size())}')
        conn.commit()
    finally:
        final = db_size()
        print(f'Done. Inserted {inserted} rows.')
        print('Final DB size:', human_readable(final))
        conn.close()


if __name__ == '__main__':
    main()
