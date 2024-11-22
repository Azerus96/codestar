import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env (для локальной разработки)
load_dotenv()

# Получение токена Hugging Face из переменной окружения
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

if not HUGGING_FACE_API_KEY:
    raise ValueError("Необходимо установить переменную окружения HUGGING_FACE_API_KEY")
