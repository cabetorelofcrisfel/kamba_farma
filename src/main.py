import sys
from pathlib import Path

def main():
    # garantir que a pasta `src` está no path para imports internos
    src_dir = Path(__file__).resolve().parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        from ui.login_window import LoginWindow
        from PyQt5.QtWidgets import QApplication
    except Exception as e:
        print('Erro ao importar módulos GUI:', e)
        print('Verifique se o PyQt5 está instalado: pip install pyqt5')
        sys.exit(1)

    app = QApplication(sys.argv)
    w = LoginWindow()
    w.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
