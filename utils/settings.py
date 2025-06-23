from dotenv import load_dotenv
import os

settings = load_dotenv()
CS2_BASE_DIR = os.getenv("CS2_BASE_DIR")
print(CS2_BASE_DIR)