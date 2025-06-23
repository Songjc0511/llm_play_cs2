import sys
import os
import time
import threading
from queue import Queue


from move.a_star import astar, load_areas, compute_centroids
from move.aim_target_point import get_target_point_direction
from move.get_viewangle import move_mouse_to_angle
from utils.check_area import AreaChecker
from getpos import get_pos
import matplotlib.pyplot as plt
import json
from matplotlib.path import Path
import numpy as np
import pyautogui
import pymem
import random
import keyboard

dwViewAngles = 27734976

# 加载路径点数据
with open(r"C:\Users\win11\Desktop\sjc\aics\files\json\path_points.json", "r") as f:
    path_points_data = json.load(f)

def pick_a_path(current_location, target_location, neighbors, costs, centroids):
    print(f"从{current_location}到{target_location}的路径")
    print(f"当前区域是否在邻居列表中：{current_location in neighbors}")
    print(f"目标区域是否在邻居列表中：{target_location in neighbors}")
    total_cost, path = astar(current_location, target_location, neighbors, costs, centroids)
    print(f"路径: {path}")
    if path is None:
        print("警告：astar 返回了 None 路径")
        return None
    return path

def get_path_points(start_area, middle_area, end_area):
    """获取从起点经过中间点到终点的所有路径点"""
    for path_data in path_points_data:
        if (path_data["StartArea"] == start_area and 
            path_data["MiddleArea"] == middle_area and 
            path_data["EndArea"] == end_area):
            return path_data["PathPoints"]
    return None

def normalize_angle(angle):
    """将角度标准化到 -180 到 180 度之间"""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle

def get_shortest_angle(current_angle, target_angle):
    """获取从当前角度到目标角度的最短旋转角度"""
    diff = normalize_angle(target_angle - current_angle)
    return diff

def mouse_movement_thread(movement_queue):
    last_move_time = time.time()
    while True:
        if not movement_queue.empty():
            current_view_x, current_view_y, target_angle = movement_queue.get()
            
            # 计算最短旋转角度
            current_angle = current_view_y
            angle_diff = get_shortest_angle(current_angle, target_angle)
            
            # 根据角度差调整移动速度
            move_speed = min(abs(angle_diff) * 0.5, 20.0)  # 角度差越大，移动速度越快，但不超过20
            
            # 确保移动间隔至少为0.01秒
            current_time = time.time()
            if current_time - last_move_time >= 0.01:
                move_mouse_to_angle(current_view_x, current_view_y, target_angle, move_speed)
                last_move_time = current_time
                
        time.sleep(0.001)  # 小延迟以避免过度占用CPU

def main(target_area):
    path = []
    areachecker = AreaChecker()
    # 创建鼠标移动队列和线程
    movement_queue = Queue()
    mouse_thread = threading.Thread(target=mouse_movement_thread, args=(movement_queue,), daemon=True)
    mouse_thread.start()
    
    # 修改文件路径，确保与 a_star.py 使用相同的文件
    coords, neighbors, costs = load_areas("areas_with_coordinates.json")
    
    # 添加调试信息
    print("加载的区域数据：")
    print("区域列表：", list(neighbors.keys()))
    print("起点区域：", target_area)
    
    # 2. 计算质心（不再依赖 Shapely）
    centroids = compute_centroids(coords)
    print("质心数据：", centroids)
    print(type(centroids))
    print("可用区域：", sorted(list(neighbors.keys())))
    try:
        pm = pymem.Pymem("cs2.exe")
        client_base = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    except Exception:
        print("请先启动 CS2！")
        exit()
        
    # 用于跟踪当前路径点的索引
    current_path_point_index = 0
    current_path_points = None
    last_angle = None
    current_segment = 0  # 当前路径段索引
    
    while True:
        if keyboard.is_pressed("m"):
            break
        pyautogui.keyDown("w")
        pyautogui.press("j")
        
        current_X, current_Y, current_Z = get_pos()
        current_area = areachecker.check_coordinate_area(x=current_X, y=current_Y, z=current_Z)[0].strip()
        print(f"当前区域: {current_area}")

        # 如果还没有路径或者已经到达目标区域，重新规划路径
        if not path or current_area == target_area:
            if current_area == target_area:
                print("已到达目标区域，松开W键")
                pyautogui.keyUp("w")
                break
            path = pick_a_path(current_area, target_area, neighbors, costs, centroids)
            if path:
                current_path_point_index = 0
                current_path_points = None
                current_segment = 0
                last_angle = None

        if path and len(path) >= 2:
            # 获取当前路径段的信息
            if current_segment < len(path) - 1:
                current_area = path[current_segment]
                next_area = path[current_segment + 1]
                end_area = path[current_segment + 2] if current_segment + 2 < len(path) else target_area
                
                # 检查是否已经到达下一个区域
                if current_area == next_area:
                    print(f"已到达下一个区域: {next_area}")
                    current_segment += 1
                    current_path_points = None
                    current_path_point_index = 0
                    last_angle = None
                    continue
                
                # 如果还没有获取当前段的路径点，获取它们
                if current_path_points is None:
                    current_path_points = get_path_points(current_area, next_area, end_area)
                    if current_path_points:
                        # 找到距离当前位置最近的路径点作为起始点
                        min_distance = float('inf')
                        nearest_index = 0
                        for i, (x, y) in enumerate(current_path_points):
                            distance = np.sqrt((float(current_X) - x)**2 + (float(current_Y) - y)**2)
                            if distance < min_distance:
                                min_distance = distance
                                nearest_index = i
                        current_path_point_index = nearest_index
                        print(f"获取新的路径段: {current_area} -> {next_area} -> {end_area}")
                        print(f"从最近的路径点开始: {current_path_point_index + 1}/{len(current_path_points)}")

                if current_path_points:
                    # 获取当前目标点
                    target_X, target_Y = current_path_points[current_path_point_index]
                    print(f"当前目标路径点 {current_path_point_index + 1}/{len(current_path_points)}: ({target_X:.2f}, {target_Y:.2f})")
                    # 计算到目标点的角度
                    angle_deg = get_target_point_direction(float(current_X), float(current_Y), float(target_X), float(target_Y))
                    current_view_y = pm.read_float(client_base + dwViewAngles)
                    current_view_x = pm.read_float(client_base + dwViewAngles + 4)
                    
                    # 如果角度变化太大，可能需要重新调整
                    if last_angle is not None:
                        angle_diff = abs(normalize_angle(angle_deg - last_angle))
                        if angle_diff > 90:  # 如果角度变化超过90度，可能需要重新调整
                            current_path_point_index = max(0, current_path_point_index - 1)
                    
                    # 将鼠标移动任务添加到队列
                    movement_queue.put((current_view_x, current_view_y, angle_deg))
                    last_angle = angle_deg
                    
                    # 检查是否到达或越过当前路径点
                    distance = np.sqrt((float(current_X) - target_X)**2 + (float(current_Y) - target_Y)**2)
                    
                    # 计算当前位置到下一个路径点的向量
                    if current_path_point_index + 1 < len(current_path_points):
                        next_X, next_Y = current_path_points[current_path_point_index + 1]
                        # 计算当前路径点到下一个路径点的向量
                        path_vector = np.array([next_X - target_X, next_Y - target_Y])
                        # 计算当前位置到当前路径点的向量
                        current_vector = np.array([float(current_X) - target_X, float(current_Y) - target_Y])
                        
                        # 计算两个向量的点积
                        dot_product = np.dot(path_vector, current_vector)
                        
                        # 如果点积为正，说明已经越过当前路径点
                        if dot_product > 0:
                            print(f"已越过路径点 {current_path_point_index}")
                            # 移除当前路径点
                            current_path_points.pop(current_path_point_index)
                            print(f"剩余路径点数量: {len(current_path_points)}")
                            
                            if not current_path_points:  # 如果所有路径点都已移除
                                # 准备进入下一段
                                current_segment += 1
                                current_path_points = None
                                current_path_point_index = 0
                                last_angle = None
                                print(f"完成当前路径段，进入下一段: {current_segment + 1}/{len(path) - 1}")
                    elif distance < 100:  # 如果是最后一个路径点，使用距离判断
                        # 移除当前路径点
                        current_path_points.pop(current_path_point_index)
                        print(f"剩余路径点数量: {len(current_path_points)}")
                        
                        if not current_path_points:  # 如果所有路径点都已移除
                            # 准备进入下一段
                            current_segment += 1
                            current_path_points = None
                            current_path_point_index = 0
                            last_angle = None
                            print(f"完成当前路径段，进入下一段: {current_segment + 1}/{len(path) - 1}")

if __name__ == "__main__":
    main("b_site".strip())
        
        
       
        