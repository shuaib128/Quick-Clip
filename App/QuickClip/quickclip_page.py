import os
from pathlib import Path
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDialog,
    QListWidget, QListWidgetItem, QMessageBox, 
    QHBoxLayout, QPushButton, QProgressBar
)
from PyQt5.QtGui import QPixmap, QIcon
from moviepy.editor import VideoFileClip
from Utils.database import (
    get_all_cliped_video_data, delete_cliped_video_by_id
)


# Separate class for Creating thumnail
class ThumbnailWorker(QThread):
    video_signal = pyqtSignal(int, str, QIcon)

    def __init__(self, folder_path, cache):
        QThread.__init__(self)
        self.folder_path = folder_path
        # passing in the cache dictionary
        self.cache = cache
    
    def __del__(self):
        self.wait()

    def run(self):
        # Get all the video data from the database
        video_data_list = get_all_cliped_video_data()

        for video_data in video_data_list:
            try:
                video_id = video_data['id']
                video_path = video_data['video_path']

                # Check if it's a valid video format
                if video_path and video_path.endswith('.mp4') or video_path.endswith('.avi'):
                    if video_path in self.cache:
                        icon = self.cache[video_path]
                    else:
                        clip = VideoFileClip(video_path)
                        # taking thumbnail at half-second
                        clip.save_frame("temp_thumbnail.png", t=0.5)

                        pixmap = QPixmap("temp_thumbnail.png")
                        icon = QIcon(pixmap)
                        self.cache[video_path] = icon

                        clip.reader.close() 
                        clip.audio.reader.close_proc()

                    # Extract the filename from the video path
                    file_name = os.path.basename(video_path)

                    self.video_signal.emit(video_id, file_name, icon)

            except Exception as e:
                delete_cliped_video_by_id(video_id)
                print(f"Error processing {video_path}: {e}")

# File copy thread
BUFFER_SIZE = 1024 * 1024  # 1MB chunks
class FileCopyThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self, src_path, dest_path):
        super().__init__()
        self.src_path = src_path
        self.dest_path = dest_path

    def run(self):
        total_size = os.path.getsize(self.src_path)
        copied = 0
        with open(self.src_path, 'rb') as src, open(self.dest_path, 'wb') as dst:
            chunk = src.read(BUFFER_SIZE)
            while chunk:
                dst.write(chunk)
                copied += len(chunk)
                progress = (copied / total_size) * 100
                self.progress_signal.emit(int(progress))
                chunk = src.read(BUFFER_SIZE)


# Custom items for each video
class CustomListItem(QWidget):
    request_delete = pyqtSignal(int, str)  # Signal to request video deletion

    def __init__(self, video_id, icon, file_name):
        super().__init__()
        self.video_path = f"Cliped\\{file_name}"
        
        # Create the layout
        layout = QHBoxLayout(self)
        layout.addStretch(1)

        # Export button
        self.export_btn = QPushButton("Export", self)
        self.export_btn.setFixedSize(100, 25)
        self.export_btn.clicked.connect(
            lambda : self.download_to_folder(self.video_path)
        )
        layout.addWidget(self.export_btn)

        # Delete button
        self.delete_btn = QPushButton("Delete", self)
        self.delete_btn.setFixedSize(100, 25)
        self.delete_btn.clicked.connect(
            lambda: self.request_delete.emit(video_id, self.video_path)
        )
        layout.addWidget(self.delete_btn)

    # Copy the video to the downlaod folder.
    def download_to_folder(self, src_path):
        # Check if there's an ongoing copy operation
        if hasattr(self, "copy_thread") and self.copy_thread.isRunning():
            QMessageBox.warning(
                self, 
                "Warning", 
                "Please wait for the current operation to complete."
            )
            return

        # Get user's home directory
        home = Path.home()
        
        # Build the path to the Downloads folder
        downloads_path = home / "Downloads"
        
        # Create the full path for the destination file
        dest_path = downloads_path / os.path.basename(src_path)

        # Open a QDialog with a QProgressBar
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Copying...")
        layout = QVBoxLayout(self.dialog)

        # Create and set up the QProgressBar
        self.progress_bar = QProgressBar(self.dialog)
        layout.addWidget(self.progress_bar)
        self.dialog.setLayout(layout)
        self.dialog.show()

        # Create and start the file copy thread
        self.copy_thread = FileCopyThread(src_path, dest_path)
        self.copy_thread.progress_signal.connect(self.update_progress)
        self.copy_thread.finished.connect(self.copy_finished)
        self.copy_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def copy_finished(self):
        self.dialog.accept()
        self.dialog.deleteLater()
        QMessageBox.information(self, "Done", "File copied successfully!")

#Main video page
class QuickClipPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder_path = "Cliped"
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 30, 25, 0)

        label = QLabel("These are all the quick cliped videos.")
        layout.addWidget(label)

        self.listWidget = QListWidget(self)
        self.listWidget.setIconSize(QPixmap(100, 100).size())
        self.listWidget.itemClicked.connect(self.play_video)
        layout.addWidget(self.listWidget)

        layout.addStretch(1)

        self.cache = {}  # The cache dictionary

        self.thumbnail_worker = ThumbnailWorker(self.folder_path, self.cache)
        self.thumbnail_worker.video_signal.connect(self.add_video_item)

    def add_video_item(self, video_id, file_name, icon):
        item = QListWidgetItem(icon, file_name)
        self.listWidget.addItem(item)

        # Set the custom widget
        custom_widget = CustomListItem(video_id, icon, file_name)
        custom_widget.request_delete.connect(self.delete_video)  # Connect to the delete request signal
        item.setSizeHint(custom_widget.sizeHint())
        self.listWidget.setItemWidget(item, custom_widget)

    def play_video(self, item):
        video_path = os.path.join(self.folder_path, item.text())
        # Using the operating system's default media player to play the video.

        # for Windows
        if os.name == "nt":  
            os.startfile(video_path)

        # for MacOS and Linux
        else:  
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, video_path])

    def showEvent(self, event):
        self.listWidget.clear()
        if self.thumbnail_worker.isRunning():
            self.thumbnail_worker.terminate()
        self.thumbnail_worker.start()

    # Click to delete the video file from the folder and the database.
    def delete_video(self, video_id, video_path):
        # First, let's remove the video from the QListWidget
        items = self.listWidget.findItems(os.path.basename(video_path), Qt.MatchExactly)
        for item in items:
            row = self.listWidget.row(item)
            self.listWidget.takeItem(row)
            del item

        # Then, actually delete the video file.
        # Also delete from the DB.
        try:
            os.remove(video_path)
            delete_cliped_video_by_id(video_id)
            QMessageBox.information(self, "Done", "File Deleted!")
        except OSError as e:
            print(f"Error deleting {video_path}: {e}")