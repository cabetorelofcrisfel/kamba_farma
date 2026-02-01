from pathlib import Path
import shutil


def backup():
    base = Path(__file__).resolve().parents[1]
    src = base / 'database' / 'kamba_farma.db'
    dest = base / 'database' / f'kamba_farma_backup.db'
    shutil.copy2(src, dest)
    print('Backup criado:', dest)


if __name__ == '__main__':
    backup()
