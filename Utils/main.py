from Utils.record_screen import start_recording
from increase_playback_speed import speed_up_on_the_fly

if __name__ == '__main__':
    # Retrieve intervals
    retrieved_intervals = [('00:00:00', '00:00:30'), ('00:00:32', '00:00:34'),
                           ('00:00:35', '00:00:45'), ('00:00:53', '00:00:55'),
                           ('00:01:03', '00:01:05'), ('00:01:11', '00:02:15'),
                           ('00:02:28', '00:02:30'), ('00:02:54', '00:02:56'),
                           ('00:02:56', '00:03:52')]
    print(retrieved_intervals)

    try:
        start_recording()
        speed_up_on_the_fly("final_output.mp4", retrieved_intervals, 2.0)
    except:
        print("some error")
