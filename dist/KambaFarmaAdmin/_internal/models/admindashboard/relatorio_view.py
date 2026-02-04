from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class SalesReportPage(QWidget):
    """Placeholder para relatórios de vendas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(" Relatórios de Vendas\n(Implementar filtros e gráficos aqui)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
