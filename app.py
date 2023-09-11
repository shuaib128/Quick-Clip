import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QAction, QStackedWidget
)
from App.Recorder.recorder_page import RecordPage
from App.Videos.video_page import VideoPage
from App.QuickClip.quickclip_page import QuickClipPage


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Navigation Example")
        self.setGeometry(0, 0, 800, 600)
        
        # Getting the center point of the screen
        screenGeometry = QApplication.desktop().screenGeometry()
        centerX = int((screenGeometry.width() - self.width()) / 2)
        centerY = int((screenGeometry.height() - self.height()) / 2)

        # Move the window's upper-left point to the calculated position
        self.move(centerX, centerY)

        self.createMenuBar()
        self.createPages()

    def createMenuBar(self):
        menubar = self.menuBar()

        # Record Menu
        recordMenu = QAction('Record', self)
        recordMenu.triggered.connect(self.showRecordPage)
        menubar.addAction(recordMenu)

        # Videos Menu
        videoMenu = QAction('Videos', self)
        videoMenu.triggered.connect(self.showVideoPage)
        menubar.addAction(videoMenu)

        # Quick Clips Menu
        quickClipMenu = QAction('Quick Clips', self)
        quickClipMenu.triggered.connect(self.showQuickClipPage)
        menubar.addAction(quickClipMenu)

    def createPages(self):
        # Stacked Widget to hold our pages
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)

        # Create each page using a separate method
        # Add each page to the QStackedWidget
        self.recordPage = RecordPage()
        self.stackedWidget.addWidget(self.recordPage)

        self.videoPage = VideoPage()
        self.stackedWidget.addWidget(self.videoPage)

        self.quickClipPage = QuickClipPage()
        self.stackedWidget.addWidget(self.quickClipPage)

    def showRecordPage(self):
        self.stackedWidget.setCurrentIndex(0)

    def showVideoPage(self):
        self.stackedWidget.setCurrentIndex(1)

    def showQuickClipPage(self):
        self.stackedWidget.setCurrentIndex(2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())