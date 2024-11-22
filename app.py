from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import config  # Импортируем наш конфиг

app = Flask(__name__)

# Инициализация модели Hugging Face с использованием токена
model_name = "facebook/blenderbot-400M-distill"  # Пример модели
chatbot = pipeline("conversational", model=model_name, use_auth_token=config.HUGGING_FACE_API_KEY)

# Хранилище контекста
context = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global context
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Сообщение не может быть пустым"}), 400

    # Добавляем сообщение пользователя в контекст
    context.append({"role": "user", "content": user_message})

    # Генерация ответа от модели
    response = chatbot(user_message)
    bot_message = response[0]["generated_text"]

    # Добавляем ответ бота в контекст
    context.append({"role": "bot", "content": bot_message})

    return jsonify({"message": bot_message, "context": context})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
