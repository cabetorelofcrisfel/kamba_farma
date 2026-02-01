from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_FILE = BASE_DIR / 'database' / 'kamba_farma.db'
DEBUG = True
