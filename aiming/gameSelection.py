import pygetwindow
import time
import bettercam
from typing import Union

# Could be do with
# from config import *
# But we are writing it out for clarity for new devs
from config import screenShotHeight, screenShotWidth

def gameSelection() -> (bettercam.BetterCam, int, Union[int, None]):
    # Selecting the correct game window
    try:
        videoGameWindows = pygetwindow.getAllWindows()
        videoGameWindow = None
        
        # 查找 Counter-Strike 2 窗口
        for window in videoGameWindows:
            if "Counter-Strike 2" in window.title:
                videoGameWindow = window
                break
                
        if videoGameWindow is None:
            print("未找到 Counter-Strike 2 窗口，请确保游戏已启动。")
            return None
            
    except Exception as e:
        print("选择游戏窗口失败: {}".format(e))
        return None

    # Activate that Window
    activationRetries = 30
    activationSuccess = False
    while (activationRetries > 0):
        try:
            videoGameWindow.activate()
            activationSuccess = True
            break
        except pygetwindow.PyGetWindowException as we:
            print("Failed to activate game window: {}".format(str(we)))
            print("Trying again... (you should switch to the game now)")
        except Exception as e:
            print("Failed to activate game window: {}".format(str(e)))
            print("Read the relevant restrictions here: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow")
            activationSuccess = False
            activationRetries = 0
            break
        # wait a little bit before the next try
        time.sleep(3.0)
        activationRetries = activationRetries - 1
    # if we failed to activate the window then we'll be unable to send input to it
    # so just exit the script now
    if activationSuccess == False:
        return None
    print("Successfully activated the game window...")

    # Starting screenshoting engine
    window_center_x = (videoGameWindow.left + videoGameWindow.right) // 2
    window_center_y = (videoGameWindow.top + videoGameWindow.bottom) // 2
    
    left = max(0, window_center_x - (screenShotWidth // 2))
    top = max(0, window_center_y - (screenShotHeight // 2))
    
    # 确保右边界不超过屏幕宽度
    right = min(2560, left + screenShotWidth)
    # 确保下边界不超过屏幕高度
    bottom = min(1440, top + screenShotHeight)
    
    # 如果右边界或下边界被限制，重新调整左边界和上边界
    left = right - screenShotWidth
    top = bottom - screenShotHeight

    region: tuple = (left, top, right, bottom)

    # Calculating the center Autoaim box
    cWidth: int = screenShotWidth // 2
    cHeight: int = screenShotHeight // 2

    print(region)

    camera = bettercam.create(region=region, output_color="BGRA", max_buffer_len=512)
    if camera is None:
        print("Your Camera Failed! Ask @Wonder for help in our Discord in the #ai-aimbot channel ONLY: https://discord.gg/rootkitorg")
        return
    camera.start(target_fps=120, video_mode=True)

    return camera, cWidth, cHeight