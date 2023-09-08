from screeninfo import get_monitors
import pyautogui
from database import store_intervals
import time
import cv2
import numpy as np
import threading
import sounddevice as sd
from scipy.io.wavfile import write
from speach_detect import is_speaker_in_use
from combine_video_audio import combine_audio_video


"""
Initiates the screen recording process while simultaneously monitoring for any speech activity.

The function performs the following operations:
1. Sets up the necessary file paths for saving audio and video recordings.
2. Defines a nested function, `speech_detector`, responsible for continuously checking for 
    voice/speech activity during the recording process.
3. Starts the `speech_detector` function which monitors for voice activity. When voice is detected, 
    it prints "Voice detected!". In the absence of voice, it prints "Ambient noise or silence...".

File Paths:
    - avi_filename: Path to save the recorded video frames.
    - audio_filename: Path to save the recorded audio.
    - final_video_filename: Path to save the final combined audio and video output.

Note: 
This function only sets up and initiates the monitoring for voice activity. The actual screen 
recording and audio capture code is assumed to be present elsewhere in the broader context.

Raises:
    KeyboardInterrupt: The `speech_detector` function can be interrupted using a keyboard interrupt.
                        Once interrupted, it prints "Terminating...".
"""


def start_recording():
    # Initialize recording state and file paths
    is_recording_audio = True
    avi_filename = r"Frames\output.avi"
    audio_filename = r"Audio\audio_record.wav"
    final_video_filename = r"Videos\final_output.mp4"

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
    def speech_detector():
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
        print(formatted_intervals)
        store_intervals(formatted_intervals)

    """
    Records audio from the default microphone until the global variable 
    `is_recording_audio` is set to False. The audio is then written to 
    a file specified by the global variable `audio_filename`.

    Parameters:
    - None

    Returns:
    - None

    Raises:
    - RuntimeError: If there's an issue during audio streaming.
    - ValueError: If invalid arguments are provided to the InputStream or write function.
    - OSError: For issues related to microphone access or writing audio data to a file.
    - MemoryError: If too much memory is consumed during the recording process.
    - IOError: If there's an issue writing the audio data to a file.
    - NameError: If global variables or libraries aren't defined in the scope.

    Example:
    ```python
    global is_recording_audio
    is_recording_audio = True
    record_audio()  # Starts recording
    # ... (after some time)
    is_recording_audio = False  # Stops recording and saves the audio file
    ```

    Notes:
    - This function heavily relies on global variables for its behavior and output file location.
    - It's essential to set `is_recording_audio` to False when you want to stop recording.
    """
    def record_audio():
        try:
            samplerate = 44100
            audio_recording = []

            with sd.InputStream(samplerate=samplerate, channels=2) as stream:
                while is_recording_audio:
                    audio_chunk, _ = stream.read(samplerate)
                    audio_recording.append(audio_chunk)

            audio_recording = np.concatenate(audio_recording, axis=0)
            write(audio_filename, samplerate, audio_recording)

        except RuntimeError as re:
            print(f"Runtime error during streaming: {re}")
        except ValueError as ve:
            print(f"Value error: {ve}")
        except OSError as e:
            if "no default output device" in str(e) or e.errno == -9996:
                print("Error: Invalid input device (no default output device)")
            # This is an example, adjust as needed
            elif "no default input device" in str(e):
                print("Error: No microphone found!")
            else:
                print(f"OSError encountered: {e}")
        except MemoryError:
            print("Memory overflow!")
        except IOError as ioe:
            print(f"IO error while writing the audio file: {ioe}")
        except NameError as ne:
            print(f"Name error: {ne}")

    # List available monitors
    monitors = get_monitors()
    for i, monitor in enumerate(monitors):
        print(
            f"Monitor {i + 1}:",
            f"{monitor.name} -",
            f"Width: {monitor.width},",
            f"Height: {monitor.height}"
        )

    # Select a monitor by its number
    monitor_number = int(
        input("Enter the monitor you want to record: ")
    )
    selected_monitor = monitors[monitor_number - 1]

    # Calculate the monitor height and width and also inicialize the FPS=20.0
    screen_width = selected_monitor.width
    screen_height = selected_monitor.height
    SCREEN_SIZE = (screen_width, screen_height)
    fps = 20.0

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(avi_filename, fourcc, fps, SCREEN_SIZE)

    # Show that the recording has started.
    print("Recording... Press 'q' in the OpenCV window to stop.")

    # Start audio recording & speech detector on a separate thread
    audio_thread = threading.Thread(target=record_audio)
    speech_detector_thread = threading.Thread(target=speech_detector)
    audio_thread.start()
    speech_detector_thread.start()
    try:
        window_name = 'Recording'
        # Set the desired window size using cv2.resizeWindow()
        desired_width = 640
        desired_height = 480
        position_x = int((screen_width - desired_width) / 2)
        position_y = int((screen_height - desired_height) / 2)

        # Create the named window with cv2.WINDOW_GUI_NORMAL to make it non-resizable
        cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)

        # Center the imShow and resize the window
        cv2.resizeWindow(window_name, desired_width, desired_height)
        cv2.moveWindow(window_name, position_x, position_y)

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
            out.write(frame)

            # Display the recording
            cv2.imshow(window_name, frame)

            # Check for 'q' key press in the OpenCV window
            if cv2.waitKey(1) == ord('q'):
                print("Stopping recording...")
                break

    except cv2.error as e:
        print(f"OpenCV Error: {e}")
    except pyautogui.FailSafeException:
        print("PyAutoGUI Fail-Safe triggered!")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Stop the audio recording thread
        is_recording_audio = False
        audio_thread.join()
        speech_detector_thread.join()

        # Close everything properly
        out.release()
        cv2.destroyAllWindows()

        combine_audio_video(
            avi_filename,
            audio_filename,
            final_video_filename
        )
