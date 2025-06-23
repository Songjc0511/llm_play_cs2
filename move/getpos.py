import os 
import pyautogui
import time
import keyboard
import json
from utils.settings import CS2_BASE_DIR

log_path = os.path.join(CS2_BASE_DIR, "console.log")
tick = float(1/64)
coordinates = []


def get_pos():
    with open(log_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        last_line = lines[-1]
        pos = last_line.split(";")
        element = pos[0].split(" ")
        x = element[-3]
        y = element[-2]
        z = element[-1]
        return x, y, z






    
if __name__ == "__main__":
    while True:
        if keyboard.is_pressed("u"):
            while True:
                pyautogui.press("j")
                with open(log_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    last_line = lines[-1]
                    try:
                        pos = last_line.split(";")
                        element = pos[0].split(" ")
                        x = element[-3]
                        y = element[-2]
                        
                        try:
                            x = float(x)
                            y = float(y)
                            coordinates.append((x, y))
                            print(x,y)
                        except:
                            pass
                    except:
                        pass
                    if keyboard.is_pressed("p"):
                        # 读取现有数据
                        existing_data = []
                        try:
                            with open("coordinates.json", "r", encoding="utf-8") as file:
                                existing_data = json.load(file)
                        except (FileNotFoundError, json.JSONDecodeError):
                            existing_data = []
                        existing_data = []
                        # 添加新数据
                        existing_data.extend(coordinates)
                        
                        # 保存所有数据
                        with open("coordinates.json", "w", encoding="utf-8") as file:
                            json.dump(existing_data, file)
                            coordinates = []
                        break

        if keyboard.is_pressed("p"):
            break