from pathlib import Path
import sys
from pathlib import Path as _Path
# Ensure project root is on sys.path so top-level packages like `database`
# are importable when the script is executed directly from anywhere.
_ROOT = _Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from database import db
import sqlite3


def init_db():
    base = Path(__file__).resolve().parents[1]
    schema = base / 'database' / 'schema.sql'
    db_path = base / 'database' / 'kamba_farma.db'
    with sqlite3.connect(db_path) as conn:
        with open(schema, 'r') as f:
            conn.executescript(f.read())
    print('Database inicializada em', db_path)


if __name__ == '__main__':
    init_db()
