import json
import numpy as np
from matplotlib.path import Path
import time
from scipy.spatial.distance import cdist

class AreaChecker:
    def __init__(self, areas_file="areas_coordinates.json"):
        # 预加载所有区域数据
        with open(areas_file, "r", encoding="utf-8") as file:
            self.areas_data = json.load(file)
        
        # 预计算所有区域的 Path 对象和坐标数组
        self.area_paths = {}
        self.area_coordinates = {}
        for area in self.areas_data:
            coordinates = np.array(area['coordinates'], dtype=np.float64)
            self.area_paths[area['area_name']] = Path(np.column_stack((coordinates[:, 0], coordinates[:, 1])))
            self.area_coordinates[area['area_name']] = coordinates

    def _calculate_distance_to_polygon(self, point, polygon_coords):
        # 计算点到多边形所有边的距离
        point = np.array(point)
        distances = []
        
        # 计算点到所有顶点的距离
        vertex_distances = cdist([point], polygon_coords)[0]
        min_vertex_distance = np.min(vertex_distances)
        
        # 计算点到所有边的距离
        for i in range(len(polygon_coords)):
            p1 = polygon_coords[i]
            p2 = polygon_coords[(i + 1) % len(polygon_coords)]
            
            # 计算点到线段的距离
            v = p2 - p1
            w = point - p1
            c1 = np.dot(w, v)
            c2 = np.dot(v, v)
            
            if c1 <= 0:
                d = np.linalg.norm(point - p1)
            elif c2 <= c1:
                d = np.linalg.norm(point - p2)
            else:
                b = c1 / c2
                pb = p1 + b * v
                d = np.linalg.norm(point - pb)
            
            distances.append(d)
        
        return min(min(distances), min_vertex_distance)

    def check_coordinate_area(self, x, y, z):
        # 确保输入坐标是浮点数
        x = float(x)
        y = float(y)
        z = float(z)
        
        target_position = (x, y)
        found_areas = []
        
        # 使用预计算的 Path 对象进行判断
        for area_name, path in self.area_paths.items():
            if path.contains_point(target_position):
                found_areas.append(area_name)
                
        if "a_site" in found_areas and "ct_spawn" in found_areas:
            if z < 1:
                return ["ct_spawn"]
            else:
                return ["a_site"]
        elif len(found_areas) > 1:
            return [found_areas[0]]
        elif found_areas:
            return found_areas
        else:
            # 如果不在任何区域内，计算到所有区域的距离
            min_distance = float('inf')
            closest_area = None
            
            for area_name, coords in self.area_coordinates.items():
                distance = self._calculate_distance_to_polygon(target_position, coords)
                if distance < min_distance:
                    min_distance = distance
                    closest_area = area_name
            
            return [closest_area] if closest_area else []

def main():
    # 创建 AreaChecker 实例
    checker = AreaChecker()
    
    try:
        while True:
            x = float(input("请输入X坐标: "))
            y = float(input("请输入Y坐标: "))
            z = float(input("请输入Z坐标: "))
            
            start_time = time.time()
            areas = checker.check_coordinate_area(x, y, z)
            end_time = time.time()
            
            print(f"运行时间: {(end_time - start_time)*1000:.2f} 毫秒")
            
            if areas:
                print(f"坐标 ({x}, {y}, {z}) 位于以下区域：")
                for area in areas:
                    print(f"- {area}")
            else:
                print(f"坐标 ({x}, {y}, {z}) 不在任何已知区域内")
                
    except KeyboardInterrupt:
        print("\n程序已退出")
    except ValueError as e:
        print(f"输入错误：{e}")
        print("请确保输入的是有效的数字")

if __name__ == "__main__":
    main() 