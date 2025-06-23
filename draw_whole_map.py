import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path

# 读取所有区域的坐标
with open("areas_coordinates.json", "r", encoding="utf-8") as file:
    data = json.load(file)



def is_point_in_polygon(point, x, y):
    path = Path(np.column_stack((x, y)))
    return path.contains_point(point)


target_position = (100, 100)

# 判断target_position是否在data的哪个区域
for area in data:
    coordinates = np.array(area['coordinates'])
    x = coordinates[:, 0]
    y = coordinates[:, 1]
    if is_point_in_polygon(target_position, x, y):
        print(area['area_name'])




# 创建图形
plt.figure(figsize=(15, 15))

# 为每个区域设置不同的颜色
colors = ['red', 'blue', 'green', 'purple', 'orange']

# 绘制每个区域
for i, area in enumerate(data):
    coordinates = np.array(area['coordinates'])
    x = coordinates[:, 0]
    y = coordinates[:, 1]
    
    # 绘制区域边界
    plt.plot(x, y, color=colors[i % len(colors)], label=area['area_name'])
    
    # 填充区域
    plt.fill(x, y, color=colors[i % len(colors)], alpha=0.3)

# 设置图形属性
plt.title('地图区域可视化')
plt.xlabel('X 坐标')
plt.ylabel('Y 坐标')
plt.legend()
plt.grid(True)

# 保持坐标轴比例相等
plt.axis('equal')

# 显示图形
plt.show()
