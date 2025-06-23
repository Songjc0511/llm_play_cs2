# Made by im-razvan - CS2 TriggerBot W/O Memory Writing
import pymem, pymem.process, keyboard, time, os                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ;os.system("\n") #Sketchy lmaooo
from win32gui import GetWindowText, GetForegroundWindow
from win32api import mouse_event
from win32con import MOUSEEVENTF_MOVE
from random import uniform
from requests import get as g
import math
import pymem


dwViewAngles = 27743776
triggerKey = "shift"

def normalize_angle(angle):
    # 将角度标准化到 -180 到 180 度之间
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle

def calculate_shortest_path(current, target, step_size=2):
    # 计算最短路径
    diff = target - current
    
    # 处理跨越180度/-180度边界的情况
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    
    int_diff = None
    if diff <0:
        int_diff = 0-int(diff)
    else:
        int_diff = 0-int(diff)
    return int_diff*step_size

def calculate_shortest_path_verticle(current, target, step_size=2):
    diff = target - current
    diff = int(diff)
    return diff*step_size


def move_mouse_to_angle(current_x, current_y, target_x, target_y, step_size=5):
    if target_x > current_x:
        horizontal_move = calculate_shortest_path(current_x, target_x, step_size)
    else:
        horizontal_move = calculate_shortest_path(current_x, target_x, step_size) 
    if target_y < current_y:
        verticle_move = calculate_shortest_path_verticle(current_y, target_y, step_size)
    else:
        verticle_move = calculate_shortest_path_verticle(current_y, target_y, step_size)
    print(f"horizontal_move: {horizontal_move}, verticle_move: {verticle_move}")
    mouse_event(MOUSEEVENTF_MOVE,horizontal_move, verticle_move, 0, 0)

def main(expected_view_angles_y, expected_view_angles_x):
    print(f"[-] TriggerBot started.\n[-] Trigger key: {triggerKey.upper()}")
    try:
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    except:
        os.system("cls") if os.name=="nt"else os.system("clear")
        print("Please open CSGO 2!")
        exit()
    
    while True:
        if keyboard.is_pressed(triggerKey):
            view_angles_y = pm.read_float(client + dwViewAngles)
            view_angles_x = pm.read_float(client + dwViewAngles + 4)
            # print(f"Current angles: X={view_angles_x:.2f}, Y={view_angles_y:.2f}")
            
            # 移动鼠标到目标角度，使用更小的步长
            move_mouse_to_angle(view_angles_x, view_angles_y, expected_view_angles_x, expected_view_angles_y)
            
        time.sleep(0.01)  # 添加小延迟以避免过度占用CPU

if __name__ == '__main__':
    main(7, 165)