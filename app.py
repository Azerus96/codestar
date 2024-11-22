from flask import Flask, render_template, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = Flask(__name__)

# Загружаем токенизатор и модель
print("Загружаем модель и токенизатор...")
tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoder")
model = AutoModelForCausalLM.from_pretrained("bigcode/starcoder")

# Если доступен GPU, переносим модель на GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
print(f"Модель загружена на устройство: {device}")


def generate_code(input_text, max_length=150, temperature=0.7, top_p=0.9, top_k=50, num_return_sequences=1):
    """
    Генерирует код на основе входного текста с использованием настроек генерации.
    """
    # Токенизация текста
    inputs = tokenizer(input_text, return_tensors="pt").to(device)

    # Генерация текста
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        num_return_sequences=num_return_sequences,
        pad_token_id=tokenizer.eos_token_id  # Указываем токен для окончания текста
    )

    # Декодируем все варианты
    generated_texts = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
    return generated_texts


@app.route("/")
def index():
    """
    Главная страница с формой для ввода запросов.
    """
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """
    Обрабатывает запросы на генерацию кода.
    """
    # Получаем входной текст от пользователя
    user_input = request.json.get("input_text")
    if not user_input:
        return jsonify({"error": "Пожалуйста, введите текст запроса."}), 400

    # Настройки генерации (можно изменить по запросу)
    max_length = request.json.get("max_length", 150)
    temperature = request.json.get("temperature", 0.7)
    top_p = request.json.get("top_p", 0.9)
    top_k = request.json.get("top_k", 50)
    num_return_sequences = request.json.get("num_return_sequences", 1)

    try:
        # Генерация кода
        generated_texts = generate_code(
            input_text=user_input,
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_return_sequences=num_return_sequences
        )

        # Возвращаем результат
        return jsonify({"generated_texts": generated_texts})

    except Exception as e:
        return jsonify({"error": f"Ошибка генерации: {str(e)}"}), 500


if __name__ == "__main__":
    # Запуск Flask-сервера
    app.run(host="0.0.0.0", port=5000, debug=True)
