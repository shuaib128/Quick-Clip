import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox,
    QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import threading
from screeninfo import get_monitors
from Utils.record_screen import start_recording
from Utils.audio_devices import list_audio_devices


class RecordPage(QWidget):
    # Define a custom signal that will take a numpy array
    # (i.e., the frame) as an argument
    update_frame_signal = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.stop_event = threading.Event()
        self.monitors = get_monitors()
        self.devices = list_audio_devices()

        # Setting margins: left, top, right, bottom
        layout.setContentsMargins(25, 30, 25, 0)

        # Combo label
        label_combo = QLabel("Select a monitor (Default monitor 0)")
        layout.addWidget(label_combo)

        # Create a QComboBox
        self.combo = QComboBox(self)
        self.combo.setFixedSize(100, 25)
        for i, monitor in enumerate(self.monitors):
            self.combo.addItem(f"Monitor {i}")
        # Add widgets to the layout
        layout.addWidget(self.combo)

        # Default selection for monitor
        self.selected_monitor = 0

        # Update selected_monitor every time the
        # combo box selection changes
        self.combo.currentIndexChanged.connect(self.update_selected_monitor)
        self.update_selected_monitor()

        # Add a gap (spacing) of 20 units
        layout.addSpacing(20)

        # Combo label for the microphone
        label_microphone = QLabel("Select a Microphone (Default 0)")
        layout.addWidget(label_microphone)

        # Create a QComboBox for microphone
        self.combo_microphone = QComboBox(self)
        self.combo_microphone.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.combo_microphone.setMinimumWidth(100)
        self.combo_microphone.setFixedHeight(25)

        for i, device in enumerate(self.devices, start=1):
            self.combo_microphone.addItem(device)
        # Add widgets to the layout
        layout.addWidget(self.combo_microphone)

        # Default selection for monitor
        self.selected_microphone = self.devices[0]

        # Update selected_monitor every time the
        # combo box selection changes
        self.combo_microphone.currentIndexChanged.connect(self.update_selected_mocrophone)
        self.update_selected_mocrophone()

        # Add a gap (spacing) of 20 units
        layout.addSpacing(20)

        label = QLabel("Clcik here to start recording")
        layout.addWidget(label)

        # Create a horizontal layout for the start record and stop button
        h_button_box = QHBoxLayout()

        # Adding the recording button
        self.start_button = QPushButton("Screen Record")
        self.start_button.setFixedSize(100, 25)
        self.start_button.clicked.connect(self.startScreenRecording)
        h_button_box.addWidget(self.start_button)

        # Adding the stop recording button
        self.stop_btn = QPushButton('Stop Recording', self)
        self.stop_btn.setFixedSize(100, 25)
        self.stop_btn.clicked.connect(self.stopScreenRecording)
        self.stop_btn.setDisabled(True)
        h_button_box.addWidget(self.stop_btn)

        # Add stretch to push buttons to the left
        h_button_box.addStretch(1)
        # Add the horizontal layout to the main vertical layout
        layout.addLayout(h_button_box)

        # Add a gap (spacing) of 20 units
        layout.addSpacing(30)

        # Add QLabel for displaying the frame
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label, 1)

        # Set size policy for image_label
        self.image_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.image_label.setAlignment(Qt.AlignCenter)

        # Connect the signal to the slot
        self.update_frame_signal.connect(self.set_frame)

        # This stretch will push all the above widgets to the top
        layout.addStretch(1)

    # Update the selected monitor based on the combo box index
    def update_selected_monitor(self):
        self.selected_monitor = self.combo.currentIndex()

    # Update the selected microphone based on the combo_microphone box index
    def update_selected_mocrophone(self):
        self.selected_microphone = self.combo_microphone.currentText()

    # Start recording thread
    def startScreenRecording(self):
        self.image_label.show()
        self.start_button.setDisabled(True)
        self.stop_btn.setDisabled(False)

        self.recording_thread = threading.Thread(
            target=start_recording,
            args=(
                self.stop_event,
                self.selected_monitor,
                self.selected_microphone,
                self.update_frame_signal
            )
        )
        self.recording_thread.start()

    # Stop the recording thread
    def stopScreenRecording(self):
        self.image_label.hide()
        self.stop_btn.setDisabled(True)
        self.start_button.setDisabled(False)

        self.stop_event.set()
        # Wait for the recording thread to finish
        self.recording_thread.join()
        # Clear the event after stopping the recording
        self.stop_event.clear()

    # Converts and sets the frame to the QLabel
    def set_frame(self, frame):
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Store the frame for resizing later
        self.current_frame = frame
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888
        )
        pixmap = QPixmap.fromImage(q_image)

        # Scale the QPixmap to fit the QLabel's current size
        # while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio
        )
        self.image_label.setPixmap(scaled_pixmap)

    # Custom resive event for current_frame
    def resizeEvent(self, event):
        if hasattr(self, 'current_frame'):
            self.set_frame(self.current_frame)
        super().resizeEvent(event)
