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


# import subprocess
# import os

# timestamps = [('00:00:00', '00:00:30'), ('00:00:32', '00:00:34'),
#               ('00:00:35', '00:00:45'), ('00:00:53', '00:00:55'),
#               ('00:01:03', '00:01:05'), ('00:01:11', '00:02:15'),
#               ('00:02:28', '00:02:30'), ('00:02:54', '00:02:56'),
#               ('00:02:56', '00:03:52')]

# input_file = "Videos/final_output.mp4"
# output_file = "output.mp4"

# # This list will store the paths to the segments
# segments = []

# start_of_video = '00:00:00'

# for start, end in timestamps:
#     normalized_start = start.replace(":", "_")
#     normalized_end = end.replace(":", "_")

#     # Extract normal speed part
#     normal_speed_segment = f"temp_{normalized_start}_normal.mp4"
#     subprocess.run(["ffmpeg", "-i", input_file, "-ss", start_of_video,
#                    "-to", start, "-c", "copy", normal_speed_segment])
#     segments.append(normal_speed_segment)

#     # Extract and speed up segment
#     fast_speed_segment = f"temp_{normalized_start}_to_{normalized_end}_fast.mp4"
#     subprocess.run(["ffmpeg", "-i", input_file, "-ss", start, "-to", end,
#                    "-vf", "setpts=0.5*PTS", "-af", "atempo=2", fast_speed_segment])
#     segments.append(fast_speed_segment)

#     start_of_video = end

# # Concatenate segments
# concat_string = "|".join(segments)
# subprocess.run(
#     ["ffmpeg", "-i", f"concat:{concat_string}", "-c", "copy", output_file])

# # Clean up temporary files
# for segment in segments:
#     os.remove(segment)
