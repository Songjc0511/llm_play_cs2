#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import heapq
import math

def clean_area_name(name: str) -> str:
    """清理区域名称，去除首尾空格"""
    return name.strip()

def load_areas(json_path):
    """
    读取 JSON，返回三个字典：
      - coords[name]    = list of [x,y] coordinates
      - neighbors[name] = list of neighbor area_names
      - costs[name]     = distance cost for edges entering this node
    JSON 格式示例（扁平数组）：
    [
      {
        "area_name": "a_door",
        "coordinates": [[x1,y1], [x2,y2], …],
        "neighbors": ["a_door_outside","a_door_t_spawn"],
        "distance": 10
      },
      …
    ]
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    coords    = {}
    neighbors = {}
    costs     = {}
    for entry in data:
        name = clean_area_name(entry['area_name'])
        coords[name]    = entry.get('coordinates', [])
        neighbors[name] = [clean_area_name(nb) for nb in entry.get('neighbors', [])]
        costs[name]     = entry.get('distance', 1.0)
    return coords, neighbors, costs

def compute_centroids(coords: dict[str, list[list[float]]]):
    """
    通过简单平均(x,y)计算质心，避免 Shapely 对空列表或点数不足时抛错
    """
    centroids = {}
    for name, pts in coords.items():
        if not pts:
            # 如果确实没有坐标，可以：
            # 1) 抛错：raise ValueError(f"No coordinates for area {name}")
            # 2) 或者给一个默认值，这里我用 (0,0)
            print(f"⚠️ 警告: 区域 '{name}' 没有坐标，质心设为 (0,0)")
            centroids[name] = (0.0, 0.0)
        else:
            xs, ys = zip(*pts)
            centroids[name] = (sum(xs) / len(xs), sum(ys) / len(ys))
    return centroids

def heuristic(u: str, v: str, centroids: dict[str, tuple[float, float]]):
    """启发式：两区域质心之间的欧氏距离"""
    try:
        x1, y1 = centroids[u]
        x2, y2 = centroids[v]
        return math.hypot(x1 - x2, y1 - y2)
    except KeyError as e:
        missing_area = str(e).strip("'")
        raise KeyError(f"区域 '{missing_area}' 在坐标数据中不存在。请检查区域名称是否正确。") from e

def astar(start: str, goal: str,
          neighbors: dict[str, list[str]],
          costs: dict[str, float],
          centroids: dict[str, tuple[float, float]]):
    """
    A* 搜索
    - costs[name] = 进入 name 的代价
    返回 (total_cost, path_list)；若不可达，返回 (inf, None)
    """
    # 优先队列元素：(f_score, g_score, node, path_list)
    open_set = [(heuristic(start, goal, centroids), 0.0, start, [start])]
    closed = set()

    while open_set:
        f, g, node, path = heapq.heappop(open_set)
        if node == goal:
            return g, path
        if node in closed:
            continue
        closed.add(node)

        for nb in neighbors.get(node, []):
            if nb in closed:
                continue
            g2 = g + costs.get(nb, 1.0)
            f2 = g2 + heuristic(nb, goal, centroids)
            heapq.heappush(open_set, (f2, g2, nb, path + [nb]))

    return float('inf'), None

if __name__ == "__main__":
    # 1. 加载数据
    coords, neighbors, costs = load_areas("areas_with_coordinates.json")

    # 2. 计算质心（不再依赖 Shapely）
    centroids = compute_centroids(coords)
    print(type(centroids))
    # 3. 打印可用区域，帮助确认名称
    print("可用区域：", sorted(list(neighbors.keys())))

    # 4. 输入起点和终点
    start = clean_area_name("a_long")
    goal  = clean_area_name("b_site"    )
    print(f"从{start}到{goal}的路径")

    # 5. 执行 A*
    total_cost, path = astar(start, goal, neighbors, costs, centroids)

    # 6. 输出结果
    if path is None:
        print(f"❗ 无法从 '{start}' 到 '{goal}'")
    else:
        print(f"从 '{start}' 到 '{goal}' 的最短距离路径：")
        print(" -> ".join(path))
        print(f"总距离：{total_cost}")
