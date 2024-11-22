from flask import Flask, render_template, request, jsonify
import requests
import config
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Hugging Face API URL для CodeStar
API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
HEADERS = {"Authorization": f"Bearer {config.HUGGING_FACE_API_KEY}"}

# Путь к базе данных
DB_FOLDER = "data"
DB_FILE = os.path.join(DB_FOLDER, "context.db")

# Максимальное количество сообщений в контексте
MAX_CONTEXT_LENGTH = 10  # Храним только последние 10 сообщений


# Инициализация базы данных
def init_db():
    """Создает папку для базы данных и таблицу для хранения контекста, если они не существуют."""
    os.makedirs(DB_FOLDER, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Сохранение сообщения в базу данных
def save_message(role, content):
    """Сохраняет сообщение в базу данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (role, content, timestamp)
        VALUES (?, ?, ?)
    """, (role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


# Загрузка сообщений из базы данных
def load_messages():
    """Загружает последние сообщения из базы данных."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, timestamp
        FROM messages
        ORDER BY id DESC
        LIMIT ?
    """, (MAX_CONTEXT_LENGTH,))
    rows = cursor.fetchall()
    conn.close()

    # Возвращаем сообщения в обратном порядке (от старых к новым)
    return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in reversed(rows)]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    # Получаем сообщение от пользователя
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Сообщение не может быть пустым"}), 400

    # Сохраняем сообщение пользователя в базу данных
    save_message("user", user_message)

    # Загружаем последние сообщения из базы данных
    context = load_messages()

    # Формируем запрос для модели с учетом контекста
    inputs = "\n".join([f"{item['role'].capitalize()}: {item['content']}" for item in context])
    payload = {"inputs": inputs}

    # Отправляем запрос к Hugging Face API
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code}, {response.text}")
            return jsonify({"error": "Ошибка при обращении к API Hugging Face"}), 500

        # Извлекаем сгенерированный текст из ответа
        bot_message = response.json()[0].get("generated_text", "Ошибка генерации ответа.")
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return jsonify({"error": "Ошибка при обращении к API Hugging Face"}), 500

    # Сохраняем ответ бота в базу данных
    save_message("bot", bot_message)

    # Возвращаем только последнее сообщение бота
    return jsonify({"message": bot_message})


@app.route("/save", methods=["POST"])
def save():
    """Сохраняет сообщение в файл."""
    message = request.json.get("message")
    if not message:
        return jsonify({"error": "Сообщение не может быть пустым"}), 400

    # Сохраняем сообщение в файл
    with open("saved_messages.txt", "a", encoding="utf-8") as file:
        file.write(message + "\n")

    return jsonify({"success": True, "message": "Сообщение сохранено."})


if __name__ == "__main__":
    # Инициализируем базу данных при запуске приложения
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
