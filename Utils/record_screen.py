from screeninfo import get_monitors
import pyautogui
from Utils.database import (
    store_video_data, get_last_video_data
)
import time
import cv2
import numpy as np
import threading
from Utils.speach_detect import is_speaker_in_use
import subprocess

# Initialize recording state and file paths
avi_filename = r"Frames\output.avi"
audio_filename = r"Audio\audio_record.wav"
# final_video_filename = ""

"""
Monitors audio input for speech activity and prints the status accordingly.

This function runs in a continuous loop as long as the recording is active (controlled by the global
variable `is_recording_audio`). On detecting voice activity using the `is_speaker_in_use` function, 
it prints "Voice detected!". If no voice is detected, it prints "Ambient noise or silence...".

Note:
- This function depends on a global variable `is_recording_audio` to decide when to terminate its operation.
- It also relies on the `is_speaker_in_use` function (expected to be defined elsewhere) which checks 
for voice activity.

Raises:
    KeyboardInterrupt: Allows the user to manually terminate the function's operation. Once interrupted,
                    it prints "Terminating...".
"""
def speech_detector(final_video_filename):
    try:
        no_voice_start = None
        time_stamps_no_voice = []
        start_time = time.time()

        while is_recording_audio:
            # Calculate elapsed time since recording started
            current_time = time.time()
            elapsed_time = current_time - start_time

            if is_speaker_in_use():
                print("Voice detected!")

                # Check if a silence period just ended, and if so, capture the timestamp
                if no_voice_start is not None:
                    time_stamps_no_voice.append(
                        (no_voice_start, elapsed_time))
                    no_voice_start = None
            else:
                print("Ambient noise or silence...")

                # If it's the start of a silence period, capture the start timestamp
                if no_voice_start is None:
                    no_voice_start = elapsed_time

    except KeyboardInterrupt:
        print("Terminating...")
        # Check if the last silence period hasn't ended yet
        if no_voice_start is not None:
            time_stamps_no_voice.append(
                (no_voice_start, time.time() - start_time))

    except (RuntimeError, IOError, ValueError) as e:
        print(f"An error occurred: {e}")

    # Convert the elapsed time in seconds to the HH:MM:SS format
    formatted_intervals = [(time.strftime('%H:%M:%S', time.gmtime(start)),
                            time.strftime('%H:%M:%S', time.gmtime(end)))
                           for start, end in time_stamps_no_voice]

    # Store the interval data in database
    store_video_data(formatted_intervals, final_video_filename)


ffmpeg_process = None  # Define this at a global or appropriate scope
def start_recording(stop_event, monitor_number, microphone_name, update_frame_signal):
    print(microphone_name)
    global is_recording_audio
    global ffmpeg_process  # Add this line at the beginning of the function
    monitors = get_monitors()
    is_recording_audio = True

    # Generate final filename for the final video
    latest_video_info = get_last_video_data()
    last_video_id = latest_video_info["id"] + \
        1 if len(latest_video_info) != 0 else 1
    final_video_filename = f"Videos\\final_video_{last_video_id}.mp4"

    # Calculate the monitor height and width and also initialize the FPS=20.0
    selected_monitor = monitors[monitor_number]
    screen_width = selected_monitor.width
    screen_height = selected_monitor.height
    SCREEN_SIZE = (screen_width, screen_height)
    fps = "20"

    # Define cmd for FFmpeg
    cmd = [
        'ffmpeg',
        '-f', 'gdigrab',
        '-framerate', fps,
        '-offset_x', str(selected_monitor.x),
        '-offset_y', str(selected_monitor.y),
        '-video_size', f"{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}",
        '-i', 'desktop',
        '-f', 'dshow',
        '-rtbufsize', '100M',  # Increase the buffer size
        '-i', f"audio={microphone_name}",
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-b:a', '192k',
        '-movflags', '+faststart',  # Improve playback compatibility
        '-threads', '0',
        final_video_filename
    ]

    # Start FFmpeg process:
    ffmpeg_process = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    print("Recording... Press 'q' in the OpenCV window to stop.")

    # Start audio recording & speech detector on a separate thread
    speech_detector_thread = threading.Thread(
        target=speech_detector,
        args=(
            final_video_filename,
        )
    )
    speech_detector_thread.start()

    try:
        while True:
            # Screen capture from selected monitor
            img = pyautogui.screenshot(region=(
                selected_monitor.x,
                selected_monitor.y,
                SCREEN_SIZE[0],
                SCREEN_SIZE[1]
            ))
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Emit the signal with the frame
            update_frame_signal.emit(frame)

            # Check for stop_event
            if stop_event.is_set():
                print("Stopping recording...")

                # Signal FFmpeg to terminate gracefully:
                ffmpeg_process.stdin.write(b'q')
                ffmpeg_process.stdin.flush()
                ffmpeg_process.wait()  # Wait for FFmpeg to finish

                # Stop the speech recording
                is_recording_audio = False
                speech_detector_thread.join()

                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pass
