from move.getpos import get_pos
import keyboard
from move.get_viewangle import move_mouse_to_angle
import math
import pyautogui
import pymem
import os

def get_target_point_direction(current_X, current_Y, target_X, target_Y):
    # 计算目标点相对于当前点的坐标方向
    # 往x轴正方向为0度，往y轴正方向为180度，往x轴负方向为180度，往y轴负方向为-90度
    
    # 计算目标点相对于当前点的差值
    delta_x = target_X - current_X
    delta_y = target_Y - current_Y
    
    # 使用atan2计算角度（弧度）
    angle_rad = math.atan2(delta_y, delta_x)  # 计算与x轴的夹角
    
    # 将弧度转换为角度
    angle_deg = math.degrees(angle_rad)
    
    # 调整角度以符合要求的坐标系统
    # if angle_deg < 0:
    #     angle_deg += 360
    print(f"angle_deg: {angle_deg}")
    # print(f"angle_rad: {angle_deg-360}")
    # # 将角度映射到新的坐标系统
    # if angle_deg <= 90:  # 第一象限
    #     final_angle = -angle_deg
    # elif angle_deg <= 180:  # 第二象限
    #     final_angle = -angle_deg
    # elif angle_deg <= 270:  # 第三象限
    #     final_angle = 360 - angle_deg
    # else:  # 第四象限
    #     final_angle = -angle_deg
        


    return angle_deg


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    dwViewAngles = 27734976
    try:
        pm = pymem.Pymem("cs2.exe")
        
        client_base = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    except Exception:
        clear_console()
        print("请先启动 CS2！")
        exit()
    while True:
        if keyboard.is_pressed("L"):
            pyautogui.press("j")
            current_X, current_Y, current_Z = get_pos() # -1037.97， 2102.03
            # 将字符串转换为浮点数
            current_X = float(current_X)
            current_Y = float(current_Y)
            current_Z = float(current_Z)
            target_X, target_Y=  1477.928345, 1952.108765
            direction_angle = get_target_point_direction(current_X, current_Y, target_X, target_Y)
            current_view_y = pm.read_float(client_base + dwViewAngles)
            current_view_x = pm.read_float(client_base + dwViewAngles + 4)
            print(f"目标点相对于当前点的方向角度: {direction_angle:.2f} 度") 
            move_mouse_to_angle(current_view_x, current_view_y ,direction_angle, 0.0)
