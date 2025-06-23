import os
import dotenv
from langchain_community.chat_models import ChatTongyi


dotenv.load_dotenv()

api_keys_str = os.getenv("DASHSCOPE_API_KEYS")

model = ChatTongyi(model="qwen-turbo", api_key=api_keys_str)

def chat(message):
    response = model.invoke(message)
    return response.content




