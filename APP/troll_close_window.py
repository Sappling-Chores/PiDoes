# This file is responsible for closing of windows while watching youtube and stuff. 

import win32gui
import win32process
import win32con
import psutil
from paths import SETTINGS_FILE
from pathlib import Path
import json


def callback(hwnd, windows_list):
    windows_list.append(hwnd)
    return True

    
class close_window():
    def __init__(self, SETTINGS_FILE):
        self.settings_file = SETTINGS_FILE
        self.black_list = []
    
    def fetch_troll_setting(self):
        settings_file = Path(self.settings_file)
        try:
           if settings_file.exists():
            with open(settings_file, "r") as f:
                settings_data = json.load(f)
                is_troll = settings_data["mode"]["troll_mode"]
            return is_troll
        
        except : 
            return None 

if __name__ == "__main__":
    print(close_window.fetch_troll_setting(SETTINGS_FILE))