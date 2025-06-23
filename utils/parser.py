import pandas as pd
import matplotlib.pyplot as plt
import glob
import math

csv_file_path = "/Users/herbertsong/Desktop/sjc/aics/files/csv_files/5E PLUS TENGX.csv"


def get_round_data_tick_index(csv_file_path):
    df = pd.read_csv(csv_file_path)
    round_data_tick_index = []
    previous_x, previous_y = None, None
    current_x, current_y = None, None
    n = 0
    for x, y, tick, time in zip(df["X"], df["Y"], df["tick"], df["game_time"]):

        if previous_x is not None and previous_y is not None:
            # 计算两点之间的距离
            distance = math.sqrt((x - previous_x) ** 2 + (y - previous_y) ** 2)

            if distance > 10:
                n += 1
                round_data_tick_index.append(tick)
        current_x = x
        current_y = y
        previous_x = current_x
        previous_y = current_y

    return round_data_tick_index


def split_round_data(csv_file_path, round_data_tick_index):
    df = pd.read_csv(csv_file_path)
    round_data = []
    current_round = 0
    current_tick = round_data_tick_index[current_round]
    temp_data = []

    for _, row in df.iterrows():
        tick = row["tick"]
        if tick < current_tick:
            row["round"] = current_round
            temp_data.append(row)
        elif tick == current_tick:
            row["round"] = current_round
            # temp_data.append(row)
            current_round += 1
            if current_round < len(round_data_tick_index):
                current_tick = round_data_tick_index[current_round]
            round_data.append(temp_data)
            temp_data = []

    return round_data


if __name__ == "__main__":
    round_data_tick_index = get_round_data_tick_index(csv_file_path)
    round_data = split_round_data(csv_file_path, round_data_tick_index)
    # 保存到新的csv文件
    for i, data in enumerate(round_data):
        # 将列表转换为DataFrame
        df_round = pd.DataFrame(data)
        df_round.to_csv(f"round_{i}.csv", index=False)
