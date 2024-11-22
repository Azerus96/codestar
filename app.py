from flask import Flask, render_template, request, jsonify
import requests
import config

app = Flask(__name__)

# Hugging Face API URL для CodeStar
API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
HEADERS = {"Authorization": f"Bearer {config.HUGGING_FACE_API_KEY}"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Сообщение не может быть пустым"}), 400

    # Отправляем запрос к модели CodeStar
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"inputs": user_message}
    )

    if response.status_code != 200:
        return jsonify({"error": "Ошибка при обращении к API Hugging Face"}), 500

    # Получаем ответ от модели
    bot_message = response.json().get("generated_text", "Ошибка генерации ответа.")

    return jsonify({"message": bot_message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
