document.getElementById("send-button").addEventListener("click", async () => {
    const userInput = document.getElementById("user-input");
    const message = userInput.value.trim();

    if (!message) return;

    // Добавляем сообщение пользователя в окно чата
    addMessage("user", message);

    // Отправляем сообщение на сервер
    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    // Добавляем ответ бота в окно чата
    addMessage("bot", data.message);

    // Очищаем поле ввода
    userInput.value = "";
});

function addMessage(role, text) {
    const chatWindow = document.getElementById("chat-window");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}`;

    // Текст сообщения
    const messageText = document.createElement("span");
    messageText.innerText = text;

    // Кнопка "Сохранить"
    const saveButton = document.createElement("button");
    saveButton.innerText = "Сохранить";
    saveButton.className = "save-button";
    saveButton.onclick = () => saveMessage(text);

    messageDiv.appendChild(messageText);
    messageDiv.appendChild(saveButton);
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Прокрутка вниз
}

async function saveMessage(message) {
    const response = await fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
    });

    const data = await response.json();
    if (data.success) {
        alert("Сообщение сохранено!");
    } else {
        alert("Ошибка сохранения сообщения.");
    }
}
