#!/usr/bin/env python3
"""
SQL Database Manager
Interface gráfica para criar e gerenciar bancos de dados SQLite
"""

import sys
import os

# Add src to path
src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if src_root not in sys.path:
    sys.path.insert(0, src_root)

from PyQt5.QtWidgets import QApplication
from ui.sql_database_gui import SQLDatabaseGUI


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = SQLDatabaseGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
