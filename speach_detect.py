import pyaudio
import webrtcvad


def is_speaker_in_use():
    """
    Determines if a speaker is in use based on audio data over a defined monitoring time.

    The function utilizes the Voice Activity Detector (VAD) to differentiate between speech and
    non-speech segments within the audio data. It captures audio frames continuously for the
    duration of MONITOR_TIME and checks each frame for speech. If the number of continuous speech
    frames surpasses the defined threshold (MIN_CONTINUOUS_FRAMES), it concludes that the speaker
    is in use.

    Globals:
        continuous_speech_frames (int): The running count of consecutive frames identified as speech.
        RATE (int): The rate at which audio is captured.
        CHUNK (int): The size of each audio chunk.
        MONITOR_TIME (int): The time duration for which audio is monitored to detect speech.
        MIN_CONTINUOUS_FRAMES (int): The threshold for the number of consecutive speech frames
                                    needed to determine that a speaker is in use.

    Returns:
        bool: True if speaker is determined to be in use, False otherwise.

    Usage:
        result = is_speaker_in_use()
        if result:
            print("Speaker is in use!")
        else:
            print("Speaker is not in use or is silent.")
    """

    CHUNK = 480  # WebRTC VAD only accepts 10, 20, or 30 ms frames
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Rate must be 8000, 16000, 32000 or 48000
    VAD_MODE = 3  # VAD aggressiveness

    vad = webrtcvad.Vad(VAD_MODE)
    p = pyaudio.PyAudio()

    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )


    def read_chunk():
        return stream.read(CHUNK)


    continuous_speech_frames = 0
    MIN_CONTINUOUS_FRAMES = 10  # Adjust as needed
    try:
        MONITOR_TIME = 2  # 2 seconds; adjust as needed

        for _ in range(0, int(RATE / CHUNK * MONITOR_TIME)):
            frame = read_chunk()
            is_speech = vad.is_speech(frame, RATE)

            if is_speech:
                continuous_speech_frames += 1
            else:
                continuous_speech_frames = 0

            if continuous_speech_frames > MIN_CONTINUOUS_FRAMES:
                return True

        return False
    
    except OSError as e:
        if "no default output device" in str(e) or e.errno == -9996:
            print("Error: Invalid input device (no default output device)")
        elif "no default input device" in str(e):  # This is an example, adjust as needed
            print("Error: No microphone found!")
        else:
            print(f"OSError encountered: {e}")

    except ValueError:
        print("A ValueError occurred.")
        return False

    except TypeError:
        print("A TypeError occurred.")
        return False

    except NameError:
        print("A NameError occurred.")
        return False

    except AttributeError:
        print("An AttributeError occurred.")
        return False

    except OverflowError:
        print("An OverflowError occurred.")
        return False

    except MemoryError:
        print("A MemoryError occurred.")
        return False

    except RuntimeError:
        print("A RuntimeError occurred.")
        return False

    except Exception as e:  # A catch-all for other exceptions
        print(f"An unexpected error occurred: {str(e)}")
        return False