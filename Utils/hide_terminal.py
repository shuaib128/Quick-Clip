import sys
import os
import subprocess

def hide_terminal():
    platform = sys.platform

    if platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    elif platform == "darwin":
        # Here we're trying to hide ALL Terminal windows, which might not be what you want.
        # More refined AppleScript can target a specific Terminal window if needed.
        script = '''/usr/bin/osascript -e 'tell app "Terminal" to close (every window whose name contains ".py")' '''
        os.system(script)

    elif platform.startswith("linux"):
        # You need to have xdotool installed for this to work.
        # Find the window with the name of your script (or Terminal) and hide it.
        # This assumes your terminal contains the name of your script.
        try:
            subprocess.check_call(['xdotool', 'search', '--name', '.py', 'windowunmap', '@'])
        except subprocess.CalledProcessError:
            pass  # Window not found, which is fine.