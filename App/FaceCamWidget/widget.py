import sys
import cv2
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QImage, QPixmap


class CircularWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(250, 250)
        self.dragging = False
        self.cap = cv2.VideoCapture(0)  # Open webcam
        if not self.cap.isOpened():
            print("Could not open webcam")
            sys.exit()
        self.timer = QTimer()  # Create a timer to update the display
        self.timer.timeout.connect(self.update_display)
        self.timer.start(20)  # Update every 30 ms

    def update_display(self):
        ret, frame = self.cap.read()  # Read a frame from the webcam
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
            self.image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.repaint()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if hasattr(self, 'image'):
            pixmap = QPixmap.fromImage(self.image)
            painter.drawPixmap(self.rect(), pixmap, pixmap.rect())  # Draw webcam feed
            painter.setBrush(Qt.NoBrush)  # Clear brush
            painter.setPen(Qt.black)  # Set pen to draw border
            painter.drawEllipse(self.rect())  # Draw border

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.dragPosition)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def closeEvent(self, event):
        self.cap.release()  # Release webcam on close
