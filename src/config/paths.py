from pathlib import Path

# project root is two parents up from this file: src/config -> src -> <project root>
ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / 'database'
