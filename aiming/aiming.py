import torch
import numpy as np
import cv2
import time
import win32api
import win32con
import pandas as pd
import gc
import warnings
import bettercam
import os
from utils.general import (cv2, non_max_suppression, xyxy2xywh, scale_boxes)

# 忽略特定的警告
warnings.filterwarnings("ignore", category=FutureWarning)

# 添加目标跟踪类
class TargetTracker:
    def __init__(self):
        self.current_target = None
        self.last_target_time = 0
        self.target_switch_cooldown = 0.5  # 目标切换冷却时间（秒）
    
    def update(self, targets, center_x, center_y):
        current_time = time.time()
        
        # 如果没有目标，清除当前目标
        if len(targets) == 0:
            self.current_target = None
            return None
        
        # 计算每个目标到屏幕中心的距离
        for target in targets:
            box_center_x = (target['x1'] + target['x2']) / 2
            box_center_y = (target['y1'] + target['y2']) / 2
            target['dist'] = np.sqrt((box_center_x - center_x)**2 + (box_center_y - center_y)**2)
        
        # 按距离排序
        targets.sort(key=lambda x: x['dist'])
        
        # 如果当前没有目标，选择最近的目标
        if self.current_target is None:
            self.current_target = targets[0]
            self.last_target_time = current_time
            return self.current_target
        
        # 检查当前目标是否仍然存在
        current_target_exists = any(
            abs(t['dist'] - self.current_target['dist']) < 10 
            for t in targets
        )
        
        # 如果当前目标消失或冷却时间已过，切换到新目标
        if not current_target_exists and (current_time - self.last_target_time) > self.target_switch_cooldown:
            self.current_target = targets[0]
            self.last_target_time = current_time
        
        return self.current_target

def get_screen_info():
    """获取所有显示器的信息"""
    screens = []
    for i in range(win32api.GetSystemMetrics(win32con.SM_CMONITORS)):
        monitor_info = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[i][0])
        screens.append({
            'index': i,
            'name': f'显示器 {i+1}',
            'left': monitor_info['Monitor'][0],
            'top': monitor_info['Monitor'][1],
            'right': monitor_info['Monitor'][2],
            'bottom': monitor_info['Monitor'][3],
            'width': monitor_info['Monitor'][2] - monitor_info['Monitor'][0],
            'height': monitor_info['Monitor'][3] - monitor_info['Monitor'][1]
        })
    return screens

def select_screen():
    """让用户选择要捕获的屏幕"""
    screens = get_screen_info()
    print("\n可用的显示器：")
    for screen in screens:
        print(f"{screen['index'] + 1}. {screen['name']} ({screen['width']}x{screen['height']})")
    
    while True:
        try:
            choice = 2
            if 1 <= choice <= len(screens):
                return screens[choice - 1]
            else:
                print("无效的选择，请重试")
        except ValueError:
            print("请输入有效的数字")

def is_mouse_in_box(mouse_x, mouse_y, x1, y1, x2, y2):
    """检查鼠标是否在框内"""
    return x1 <= mouse_x <= x2 and y1 <= mouse_y <= y2

def move_mouse_to_center(x1, y1, x2, y2, center_x, center_y, step=0.5, tolerance=10):
    # 计算边界框中心点
    box_center_x = (x1 + x2) / 2
    box_center_y = (y1 + y2) / 2
    
    # 获取当前鼠标位置
    mouse_x, mouse_y = win32api.GetCursorPos()
    
    # 检查鼠标是否在框内
    if is_mouse_in_box(mouse_x, mouse_y, x1, y1, x2, y2):
        # 鼠标在框内，执行开火
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)  # 短暂延迟
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        return True
    
    # 计算需要移动的距离（修正方向）
    move_x = int((box_center_x - center_x) * step)
    move_y = int((box_center_y - center_y) * step)
    
    # 检查是否在容差范围内
    if abs(box_center_x - center_x) <= tolerance and abs(box_center_y - center_y) <= tolerance:
        # 目标已居中，按下鼠标左键
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.01)  # 短暂延迟
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        return True  # 目标已居中并开火
    else:
        # 移动鼠标
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
        return False  # 目标未居中

def main():
    # 创建images文件夹（如果不存在）
    if not os.path.exists('images'):
        os.makedirs('images')
    
    # 初始化帧计数器
    frame_count = 0
    
    # 初始化目标跟踪器
    target_tracker = TargetTracker()
    
    # 加载模型
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=r'aiming\best.pt')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    stride, names, pt = model.stride, model.names, model.pt
    print("可检测的目标类别:", names)
    
    # 选择要捕获的屏幕
    selected_screen = select_screen()
    print(f"\n已选择: {selected_screen['name']}")
    
    # 创建屏幕捕获对象，指定捕获区域
    region = (selected_screen['left'], selected_screen['top'], 
             selected_screen['right'], 1440)
    print(f"region: {region}")
    
    camera = bettercam.create(region=region, output_color="BGRA", max_buffer_len=512)
    if camera is None:
        print("创建屏幕捕获失败！")
        return
    
    camera.start(target_fps=120, video_mode=True)
    
    # 初始化中心点变量
    center_x = 2560//2
    center_y = 1440//2
    
    while True:
        with torch.no_grad():
            # 获取图像
            npImg = np.array(camera.get_latest_frame())
            # 更新中心点（因为图像大小可能变化）
            center_x = npImg.shape[1] // 2
            center_y = npImg.shape[0] // 2
            
            # 保存原始图像用于显示
            display_img = npImg.copy()
            # 调整图像大小为模型期望的尺寸
            model_input = cv2.resize(npImg, (640, 640))
            # 转换BGR到RGB
            model_input = cv2.cvtColor(model_input, cv2.COLOR_BGR2RGB)
            
            # 图像预处理
            im = torch.from_numpy(model_input).to(device)
            im = im.float()  # uint8 to float32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            # 调整维度顺序从(H,W,C)到(C,H,W)
            im = im.permute(2, 0, 1)
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim
            
            # 模型推理
            pred = model(im)
            
            # NMS后处理
            pred = non_max_suppression(pred, conf_thres=0.7, iou_thres=0.45, classes=None, agnostic=False, max_det=1000)
            if len(pred) == 0:
                print("没有检测到目标")
                
            # 处理检测结果
            valid_targets = []
            for i, det in enumerate(pred):
                if len(det):
                    # 将边界框从img_size缩放到im0大小
                    det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], model_input.shape).round()
                    
                    # 获取检测到的类别
                    detected_classes = det[:, 5].unique().int().tolist()
                    
                    # 检查是否同时存在类别0和1，或者类别1和2
                    valid_detection = (0 in detected_classes and 1 in detected_classes) or (1 in detected_classes and 2 in detected_classes)
                    
                    if valid_detection:
                        # 打印结果
                        for c in det[:, 5].unique():
                            n = (det[:, 5] == c).sum()  # 每个类别的检测数量
                            print(f"检测到 {n} 个 {names[int(c)]}")
                        
                        # 处理每个检测框
                        for *xyxy, conf, cls in reversed(det):
                            c = int(cls)  # 整数类别
                            label = f"{names[c]} {conf:.2f}"
                            if label!= 'head':
                                label = 'human'
                            
                            # 计算原始图像上的坐标
                            scale_x = npImg.shape[1] / 640
                            scale_y = npImg.shape[0] / 640
                            
                            x1 = int(xyxy[0] * scale_x)
                            y1 = int(xyxy[1] * scale_y)
                            x2 = int(xyxy[2] * scale_x)
                            y2 = int(xyxy[3] * scale_y)
                            
                            # 在原始图像上绘制边界框
                            cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(display_img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            
                            # 如果是类别1，添加到有效目标列表
                            if c == 1:
                                valid_targets.append({
                                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                                    'conf': float(conf)
                                })
                                
                                # 检查鼠标是否在当前框内
                                mouse_x, mouse_y = win32api.GetCursorPos()
                                if is_mouse_in_box(mouse_x, mouse_y, x1, y1, x2, y2):
                                    # 鼠标在框内，执行开火
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                                    time.sleep(0.01)
                                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                                    print("鼠标在目标框内，执行开火")
                                    break  # 找到一个框内目标就退出循环
            
            # 更新目标跟踪器并获取当前目标
            current_target = target_tracker.update(valid_targets, center_x, center_y)
            
            # 如果存在当前目标，进行瞄准
            if current_target is not None:
                is_centered = move_mouse_to_center(
                    current_target['x1'], current_target['y1'],
                    current_target['x2'], current_target['y2'],
                    center_x, center_y
                )
                if is_centered:
                    print("目标已居中并点击")
            
            # 显示结果
            # cv2.imshow('Detection', display_img)
            
            # 保存当前帧
            frame_path = os.path.join('images', f'frame_{frame_count:04d}.jpg')
            cv2.imwrite(frame_path, display_img)
            frame_count += 1
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
    cv2.destroyAllWindows()
    camera.stop()
        
if __name__ == '__main__':
    main()