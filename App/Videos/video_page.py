from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)


class VideoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # left, top, right, bottom
        layout.setContentsMargins(25, 30, 25, 0)
        
        label = QLabel("This is the Videos page.")
        layout.addWidget(label)

        # This stretch will push all the above widgets to the top
        layout.addStretch(1)
