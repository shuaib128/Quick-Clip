from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx

timestamps = [('00:00:00', '00:00:30'), ('00:00:32', '00:00:34'),
              ('00:00:35', '00:00:45'), ('00:00:53', '00:00:55'),
              ('00:01:03', '00:01:05'), ('00:01:11', '00:02:15'),
              ('00:02:28', '00:02:30'), ('00:02:54', '00:02:56'),
              ('00:02:56', '00:03:52')]


def time_to_seconds(timestring):
    h, m, s = map(int, timestring.split(':'))
    return h * 3600 + m * 60 + s


video = VideoFileClip(r"Videos\final_output.mp4")
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
final_clip.write_videofile("output_video.mp4")
