from pathlib import Path
import argparse
from database.db import connect, get_db_path


def has_column(conn, table, column):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [r['name'] for r in cur.fetchall()]
    return column in cols


def main():
    parser = argparse.ArgumentParser(description='Add descricao column to produtos if missing')
    parser.add_argument('--db', help='Path to DB file (optional)')
    args = parser.parse_args()

    base = Path(__file__).resolve().parents[1]
    db_path = Path(args.db) if args.db else get_db_path(base)

    if not db_path.exists():
        print(f'Database not found at {db_path}')
        return

    conn = connect(db_path)
    try:
        if has_column(conn, 'produtos', 'descricao'):
            print('Column `descricao` already exists in produtos')
            return

        print('Adding column `descricao` to produtos...')
        conn.execute('ALTER TABLE produtos ADD COLUMN descricao TEXT;')
        conn.commit()
        print('Column added successfully.')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
