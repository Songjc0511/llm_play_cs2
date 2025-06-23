import asyncio
import websockets
import json
import time

async def send_area_request(x, y, z):
    uri = "ws://192.168.124.37:6001/ws/area"
    
    
    async with websockets.connect(uri) as websocket:
        while True:
            start_time = time.time()
            # 发送坐标数据
            await websocket.send(json.dumps({"type":"get_current_area_name","x": x, "y": y, "z": z}))
            # 接收返回的区域名
            response = await websocket.recv()
            json_response = json.loads(response)
            print("收到区域名:", json_response["area"])
            end_time = time.time()
            print(end_time - start_time)
            time.sleep(2)
if __name__ == "__main__":
    # 示例坐标
    asyncio.run(send_area_request(1.0, 2.0, 3.0))