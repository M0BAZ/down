document.addEventListener('DOMContentLoaded', function () {
    // Находим элементы ввода логина и пароля
    const loginInput = document.getElementById('login');
    const passwordInput = document.getElementById('password');
    const registerButton = document.getElementById('registerButton');
    const statusMessage = document.getElementById('statusMessage');

    // Обработчик нажатия на кнопку регистрации
    registerButton.addEventListener('click', () => {
        const login = loginInput.value;
        const password = passwordInput.value;

        if (!login || !password) {
            statusMessage.textContent = "Пожалуйста, заполните все поля.";
            return;
        }

        // Отправляем сообщение в background.js для регистрации пользователя
        chrome.runtime.sendMessage({ action: "registerUser", login, password }, (response) => {
            // Проверка на наличие ошибки при отправке сообщения
            if (chrome.runtime.lastError) {
                console.error("Ошибка при отправке сообщения:", chrome.runtime.lastError);
                statusMessage.textContent = "Ошибка при подключении к серверу.";
                return;
            }

            // Проверяем, что ответ содержит свойство `success`
            if (response && response.success) {
                statusMessage.textContent = "Регистрация прошла успешно!";
            } else {
                statusMessage.textContent = response.error || "Ошибка при регистрации.";
            }
        });
    });
});
