"""Compatibilidade: exportar `FornecedorPage` apontando para a SPA de Finanças."""

try:
    from .financas import FinancasPage
except Exception:
    # Fallback: minimal placeholder if import falhar
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PyQt5.QtCore import Qt

    class FinancasPage(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            l = QVBoxLayout(self)
            lbl = QLabel("Módulo Finanças não disponível")
            lbl.setAlignment(Qt.AlignCenter)
            l.addWidget(lbl)

# Exportar com o nome esperado pelo resto do app
FornecedorPage = FinancasPage
