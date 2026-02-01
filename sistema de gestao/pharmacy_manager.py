#!/usr/bin/env python3
"""
Pharmacy Manager Setup Wizard
Main entry point for the pharmacy registration application
"""

import sys
import os

# Add src to path
src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if src_root not in sys.path:
    sys.path.insert(0, src_root)

from PyQt5.QtWidgets import QApplication
from ui.pharmacy_setup import PharmacySetupWizard


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = PharmacySetupWizard()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
