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
    messageDiv.innerHTML = text;
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
