import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json
import numpy as np
from matplotlib.path import Path
import time
from utils.check_area import *

def read_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    return df

def get_path_data(df):
    movement_trace = df[['X', 'Y', 'Z','usercmd_viewangle_y', 'usercmd_viewangle_x']].values
    print(movement_trace)

def get_start_and_end_point_randomly(df):
    start_index = np.random.randint(0, len(df))
    end_index = np.random.randint(start_index, len(df))
    start_point = df.iloc[start_index]
    end_point = df.iloc[end_index]
    return start_point, end_point

def get_path_data_between_two_points(df, start_point, end_point):
    start_index = np.where(df['X'] == start_point['X'])[0][0]
    end_index = np.where(df['X'] == end_point['X'])[0][0]
    path_data = df.iloc[start_index:end_index+1]
    return path_data

def get_start_and_end_point_area_name(df, start_point, end_point):
    start_area_name = check_coordinate_area(start_point['X'], start_point['Y'], start_point['Z'])
    end_area_name = check_coordinate_area(end_point['X'], end_point['Y'], end_point['Z'])
    return start_area_name, end_area_name

def pipeline(df):
    start_point, end_point = get_start_and_end_point_randomly(df)
    path_data = get_path_data_between_two_points(df, start_point, end_point)
    start_area_name, end_area_name = get_start_and_end_point_area_name(df, start_point, end_point)
    return path_data, start_area_name, end_area_name

def make_path_data(df):
    path_data, start_area_name, end_area_name = pipeline(df)
    return path_data, start_area_name, end_area_name

def generate_path_dataset_from_dir(csv_dir, num_samples_per_file=100, output_file='path_dataset.json'):
    all_data = []
    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_dir, filename)
            print(f"正在处理: {file_path}")
            df = read_data(file_path)
            # 只要is_alive为true的行
            df = df[df['is_alive'] == True]
            for _ in range(num_samples_per_file):
                path_data, start_area, end_area = make_path_data(df)
                if len(path_data) < 1000:
                    continue
                record = {
                    "file": filename,
                    "start_point": path_data.iloc[0][['X', 'Y', 'Z']].tolist(),
                    "end_point": path_data.iloc[-1][['X', 'Y', 'Z']].tolist(),
                    "start_area": start_area,
                    "end_area": end_area,
                    "path": path_data[['X', 'Y', 'Z']].values.tolist(),
                    "view_angle": path_data[['usercmd_viewangle_y', 'usercmd_viewangle_x']].values.tolist(),
                    "user_wasd_cmd": [
                        [cmd for cmd, is_pressed in zip(['FORWARD', 'BACK', 'LEFT', 'RIGHT'], row) if is_pressed]
                        for row in path_data[['FORWARD', 'BACK', 'LEFT', 'RIGHT']].values
                    ]
                }
                all_data.append(record)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"所有数据已保存到 {output_file}")

if __name__ == "__main__":
    generate_path_dataset_from_dir(r"C:\Users\Win11\Desktop\sjc\aics\files\csv_files", 5, 'path_dataset.json')