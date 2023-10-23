import sounddevice as sd

def list_audio_devices():
    input_devices = []
    for i, device in enumerate(sd.query_devices()):
        if device['max_input_channels'] > 0:
            input_devices.append(device['name'])
            
    return input_devices