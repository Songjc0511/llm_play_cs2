import os
import sys
import time
# 获取项目根目录的绝对路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到Python路径中
sys.path.append(project_root)
os.environ['PYTHONPATH'] = 'C:\\Users\\31789\\Desktop\\sjc\\aics\\data_processing'

from move.a_star import astar, load_areas, compute_centroids
coords, neighbors, costs = load_areas("areas_with_coordinates.json")
from utils.check_area import AreaChecker
from move.getpos import get_pos
import keyboard
from pydantic import BaseModel
import json
import itertools

class PathPointClass(BaseModel):
    StartArea: str
    MiddleArea: str
    EndArea: str
    PathPoints: list[tuple[float, float]]

path_points_json = []

def get_all_possible_paths():
    """获取所有可能的路径组合"""
    all_areas = list(neighbors.keys())
    paths = []
    
    # 遍历所有可能的起点
    for start in all_areas:
        # 获取起点的所有邻居作为中间点
        for middle in neighbors[start]:
            # 获取中间点的所有邻居作为终点（排除起点）
            for end in neighbors[middle]:
                if end != start:
                    paths.append((start, middle, end))
    
    return paths

def insert_path_point(start_area, middle_area, end_area, path_points):
    global path_points_json
    # 确保区域名称是字符串
    if isinstance(start_area, list):
        start_area = start_area[0]
    if isinstance(middle_area, list):
        middle_area = middle_area[0]
    if isinstance(end_area, list):
        end_area = end_area[0]
        
    new_point = PathPointClass(
        StartArea=str(start_area),
        MiddleArea=str(middle_area),
        EndArea=str(end_area),
        PathPoints=path_points
    )
    
    # 检查是否已存在相同的路径
    for point in path_points_json:
        if (point.StartArea == new_point.StartArea and 
            point.MiddleArea == new_point.MiddleArea and
            point.EndArea == new_point.EndArea):
            return
            
    path_points_json.append(new_point)
    with open("files/json/path_points.json", "w") as f:
        json.dump([point.model_dump() for point in path_points_json], f, indent=4)

if __name__ == "__main__":
    area_checker = AreaChecker()
    
    # 获取所有可能的路径组合
    all_paths = get_all_possible_paths()
    current_path_index = 0
    
    print(f"总共有 {len(all_paths)} 条可能的路径需要记录")
    print("按c获取连接点位置,按v添加路径点,按x保存当前路径")
    print("按n切换到下一条路径,按b返回上一条路径,按q退出")
    
    # 用于跟踪按键状态
    key_states = {
        'c': False,
        'v': False,
        'x': False,
        'n': False,
        'b': False,
        'q': False
    }
    
    # 用于存储当前路径的数据
    current_path_points = []
    
    def show_current_path():
        if current_path_index < len(all_paths):
            start, middle, end = all_paths[current_path_index]
            print(f"\n当前需要记录的路径 ({current_path_index + 1}/{len(all_paths)}):")
            print(f"起点: {start} -> 中间: {middle} -> 终点: {end}")
        else:
            print("\n所有路径都已记录完成！")
    
    show_current_path()
    
    while True:
        # 检查q键退出
        if keyboard.is_pressed("q") and not key_states['q']:
            key_states['q'] = True
            print("程序退出")
            break
        elif not keyboard.is_pressed("q"):
            key_states['q'] = False
            
        # 切换到下一条路径
        if keyboard.is_pressed("n") and not key_states['n']:
            key_states['n'] = True
            if current_path_index < len(all_paths) - 1:
                current_path_index += 1
                current_path_points = []
                show_current_path()
            else:
                print("已经是最后一条路径了")
        elif not keyboard.is_pressed("n"):
            key_states['n'] = False
            
        # 返回上一条路径
        if keyboard.is_pressed("b") and not key_states['b']:
            key_states['b'] = True
            if current_path_index > 0:
                current_path_index -= 1
                current_path_points = []
                show_current_path()
            else:
                print("已经是第一条路径了")
        elif not keyboard.is_pressed("b"):
            key_states['b'] = False
            
        # 获取连接点位置
        if keyboard.is_pressed("c") and not key_states['c']:
            key_states['c'] = True
            print("获取连接点位置...")
            keyboard.press_and_release("j")
            time.sleep(0.1)
            pos_x, pos_y, pos_z = get_pos()
            current_path_points.append((pos_x, pos_y))  # 将连接点添加到路径点列表
            print(f"连接点位置: ({pos_x}, {pos_y})")
        elif not keyboard.is_pressed("c"):
            key_states['c'] = False
            
        # 获取路径点位置
        if keyboard.is_pressed("v") and not key_states["v"]:
            key_states["v"] = True
            print("获取路径点位置...")
            keyboard.press_and_release("j")
            time.sleep(0.1)
            pos_x, pos_y, pos_z = get_pos()
            current_path_points.append((pos_x, pos_y))
            print(f"路径点位置: ({pos_x}, {pos_y})")
        elif not keyboard.is_pressed("v"):
            key_states["v"] = False

        # 保存路径点
        if keyboard.is_pressed('x') and not key_states['x']:
            key_states['x'] = True
            if len(current_path_points) >= 2:  # 确保至少有一个连接点和一个路径点
                start, middle, end = all_paths[current_path_index]
                print("保存路径点数据...")
                insert_path_point(start, middle, end, current_path_points)
                print("保存完成")
                # 自动切换到下一条路径
                if current_path_index < len(all_paths) - 1:
                    current_path_index += 1
                    current_path_points = []
                    show_current_path()
                else:
                    print("所有路径都已记录完成！")
            else:
                print("请先获取连接点和至少一个路径点")
        elif not keyboard.is_pressed('x'):
            key_states['x'] = False
