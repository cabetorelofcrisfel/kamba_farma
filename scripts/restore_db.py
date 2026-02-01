from pathlib import Path
import shutil


def restore(backup_path=None):
    base = Path(__file__).resolve().parents[1]
    dest = base / 'database' / 'kamba_farma.db'
    if backup_path is None:
        backup_path = base / 'database' / 'kamba_farma_backup.db'
    shutil.copy2(backup_path, dest)
    print('Restaurado para:', dest)


if __name__ == '__main__':
    restore()
