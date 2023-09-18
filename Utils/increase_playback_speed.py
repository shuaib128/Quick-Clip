from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from Utils.database import store_cliped_video_data


def time_to_seconds(timestring):
    h, m, s = map(int, timestring.split(':'))
    return h * 3600 + m * 60 + s


def start_increase_timestamps(filename, video_path, timestamps):
    video = VideoFileClip(video_path)
    clips = []
    previous_end = 0

    for start, end in timestamps:
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