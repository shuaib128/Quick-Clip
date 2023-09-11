from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)


class QuickClipPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # left, top, right, bottom
        layout.setContentsMargins(25, 0, 25, 0)
        
        label = QLabel("This is the Quick Clips page.")
        layout.addWidget(label)
