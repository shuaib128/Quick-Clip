import sys

def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')