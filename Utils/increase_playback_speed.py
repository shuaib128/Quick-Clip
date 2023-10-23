from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from Utils.database import store_cliped_video_data


# This function takes a time string in the format "hh:mm:ss" 
# and adds the specified number of seconds to it.
# The result is returned in the same format.
def add_seconds_to_time(timestring, seconds):
    h, m, s = map(int, timestring.split(':'))
    total_seconds = h * 3600 + m * 60 + s + seconds
    h_new = total_seconds // 3600
    m_new = (total_seconds % 3600) // 60
    s_new = total_seconds % 60
    return f"{h_new:02}:{m_new:02}:{s_new:02}"


# This function calculates the time difference in seconds between two time strings.
def time_difference(start_str, end_str):
    start_seconds = time_to_seconds(start_str)
    end_seconds = time_to_seconds(end_str)
    return end_seconds - start_seconds

# This function converts a time string in the format "hh:mm:ss" to seconds.
def time_to_seconds(timestring):
    h, m, s = map(int, timestring.split(':'))
    return h * 3600 + m * 60 + s


def start_increase_timestamps(filename, video_path, timestamps):
    video = VideoFileClip(video_path)
    clips = []
    previous_end = 0

    adjusted_timestamps = []
    for i, (start, end) in enumerate(timestamps):
        if i < len(timestamps) - 1:  # If it's not the last pair
            start = add_seconds_to_time(start, 3)
        
        if time_difference(start, end) >= 5:
            adjusted_timestamps.append((start, end))

    for start, end in adjusted_timestamps:
        start_sec = time_to_seconds(start)
        end_sec = time_to_seconds(end)

        # Add segment before fast-forwarding part
        if start_sec > previous_end:
            clips.append(video.subclip(previous_end, start_sec))

        # Fast-forwarding part
        # Fast-forwards the clip at 2x speed. Adjust as needed.
        clip = video.subclip(start_sec, end_sec).fx(vfx.speedx, factor=6)
        clips.append(clip)

        previous_end = end_sec

    # Add remaining segment of the video after the last timestamp
    if previous_end < video.duration:
        clips.append(video.subclip(previous_end, video.duration))

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(f"Cliped\\cliped_{filename}")

    # Write in database
    store_cliped_video_data(f"Cliped\\cliped_{filename}")