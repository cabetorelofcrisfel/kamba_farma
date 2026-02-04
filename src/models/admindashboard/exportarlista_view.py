from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ExportListPage(QWidget):
    """Placeholder para exportação de listas de produtos."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(" Exportar Lista\n(Implementar opções de exportação CSV/XLS)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
