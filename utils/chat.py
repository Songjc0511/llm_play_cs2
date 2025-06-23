import os
import dotenv
from langchain_community.chat_models import ChatTongyi


dotenv.load_dotenv()

api_keys_str = os.getenv("DASHSCOPE_API_KEYS")

model = ChatTongyi(model="qwen-turbo", api_key=api_keys_str)

def chat(message):
    response = model.invoke(message)
    return response.content


def get_target_area(if_have_c4, current_area_name, left_time):
    message = f"""你是一个电子竞技教练，玩家正在玩cs2，dust2地图。
    玩家当前位置为{current_area_name}
    玩家当前是否拥有C4：{if_have_c4}
    玩家当前剩余时间：{left_time}
    请根据玩家当前状态，给出玩家下一步应该去的位置
    
    """
    response = model.invoke(message)
    return response.content

