import re
import subprocess


def timestamp_to_seconds(timestamp):
    """
    Convert a timestamp in the format "HH:MM:SS.sss" to seconds.
    Parameters:
    - timestamp (str): The timestamp in "HH:MM:SS.sss" format.
    Returns:
    - float: The time in seconds.
    """
    hours, minutes, rest = re.split(':', timestamp)
    seconds, milliseconds = map(float, re.split('\.', rest))
    return (
        int(hours) *
        3600 +
        int(minutes) *
        60 +
        seconds +
        milliseconds /
        100
    )


def calculate_adjustment_factor(current_timestamp, desired_timestamp):
    """
    Calculate the adjustment factor based on two timestamps.
    Parameters:
    - current_timestamp (str): The current duration in "HH:MM:SS.sss" format.
    - desired_timestamp (str): The desired duration in "HH:MM:SS.sss" format.
    Returns:
    - float: The factor by which the current duration should be multiplied 
             to match the desired duration.
    """
    current_duration = timestamp_to_seconds(current_timestamp)
    desired_duration = timestamp_to_seconds(desired_timestamp)

    return (1 / (desired_duration / current_duration))


def get_video_duration(file_path):
    """
    Extract the duration of a video using FFmpeg.
    Parameters:
    - file_path (str): Path to the video file.
    Returns:
    - str: The duration of the video in the format "HH:MM:SS.ss". 
           Returns None if the duration couldn't be extracted.
    """
    cmd = ['ffmpeg', '-i', file_path]

    # Run the command and get the stderr (where FFmpeg outputs the info)
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    output = result.stderr

    # Use a regex to extract the duration
    duration_match = re.search(
        r"Duration: (\d{2}:\d{2}:\d{2}\.\d{2})",
        output
    )

    if duration_match:
        return duration_match.group(1)
    else:
        return None


def get_audio_duration(file_path):
    """
    Extract the duration of a audio using FFmpeg.
    Parameters:
    - file_path (str): Path to the audio file.
    Returns:
    - str: The duration of the audio in the format "HH:MM:SS.ss". 
           Returns None if the duration couldn't be extracted.
    """
    cmd = ['ffmpeg', '-i', file_path]

    # Run the command and get the stderr (where FFmpeg outputs the info)
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    output = result.stderr

    # Use a regex to extract the duration
    duration_match = re.search(
        r"Duration: (\d{2}:\d{2}:\d{2}\.\d{2})",
        output
    )

    if duration_match:
        return duration_match.group(1)
    else:
        return None


def combine_audio_video(video_filename, audio_filename, output_filename):
    """
    Combine a video and audio file with an option to adjust the video speed based on the durations.
    The function will calculate the required adjustment to the video's speed to match the audio's duration.
    Parameters:
    - video_filename (str): Path to the input video file.
    - audio_filename (str): Path to the input audio file.
    - output_filename (str): Path to the desired output file.
    """

    # Get the duration of the video and audio files
    video_duration = get_video_duration(video_filename)
    audio_duration = get_audio_duration(audio_filename)

    # Calculate the factor by which the video needs to be adjusted to match the audio's duration
    slowdown_factor = calculate_adjustment_factor(
        audio_duration,
        video_duration
    )

    # If slowdown_factor is not 1, then modify the video stream using the setpts filter
    video_filter = f'setpts={slowdown_factor}*PTS' if slowdown_factor != 1.0 else None

    # Initialize the FFmpeg command with input video and audio files
    command = [
        'ffmpeg',
        '-i', video_filename,  # Input video file
        '-i', audio_filename  # Input audio file
    ]

    # Add video filter if slowdown factor is provided
    if video_filter:
        command.extend(['-vf', video_filter])
        command.extend(['-c:v', 'libx264'])  # Specify the video codec
    else:
        command.extend(['-c:v', 'copy'])

    # Add additional command options to re-encode the audio and specify the output file
    command.extend([
        '-c:a', 'aac',  # Re-encode audio to aac format
        '-strict', 'experimental',
        output_filename  # Output file
    ])

    # Execute the FFmpeg command
    subprocess.run(command)
