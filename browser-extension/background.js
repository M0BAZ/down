const webServerHost = 'http://localhost:8001'; //

// Функция для сохранения учетных данных пользователя в localStorage
function saveCredentials(username, password) {
    localStorage.setItem("username_mirea_user", username);
    localStorage.setItem("password_mirea_user", password);
}

// Функция для получения учетных данных пользователя из localStorage
function getCredentials() {
    return {
        username: localStorage.getItem("username_mirea_user"),
        password: localStorage.getItem("password_mirea_user")
    };
}

// Функция для регистрации пользователя на сервере
async function registerUser(username, password) {
    try {
        const response = await fetch(`${webServerHost}/register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok) {
            saveCredentials(username, password);
            console.log("Пользователь успешно зарегистрирован.");
        } else {
            console.error("Ошибка регистрации:", data);
        }
    } catch (error) {
        console.error("Ошибка сети при регистрации:", error);
    }
}

// Проверка, есть ли учетные данные пользователя
chrome.runtime.onInstalled.addListener(() => {
    const { username, password } = getCredentials();
    if (!username || !password) {
        const user = prompt("Введите имя пользователя для регистрации:");
        const pass = prompt("Введите пароль:");

        if (user && pass) {
            registerUser(user, pass);
        }
    }
});


chrome.webNavigation.onCompleted.addListener((details) => {

    const url = details.url;

    // Шаблон для страницы с "action=view"
    const viewPattern = /https:\/\/online-edu\.mirea\.ru\/mod\/assign\/view\.php.*action=view.*/;
    if (!viewPattern.test(url)) {
        return;
    }

    console.log("Страница соответствует шаблону 'action=view'");
    const message = {action: "viewPage"};

    if (message) {
        chrome.tabs.sendMessage(details.tabId, message, (response) => {
            if (chrome.runtime.lastError) {
                console.error("Ошибка при отправке сообщения в content.js:", chrome.runtime.lastError);
            } else {
                console.log("Ответ от content.js:", response);
            }
        });
    }
}, {
    url: [{hostContains: "online-edu.mirea.ru"}]
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

    // Обработчик для получения cookies
    if (message.action === "getCookies") {
        chrome.cookies.getAll({domain: "online-edu.mirea.ru"}, (cookies) => {
            const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join("; ");
            sendResponse(cookieString);
        });
        return true;
    }

    // Обработчик для загрузки файла
    if (message.action === "downloadFile") {
        chrome.downloads.download({
            url: message.url,
            filename: message.filename,
            saveAs: false
        });
    }

    // Показ уведомления
    if (message.action === "showNotification") {
        chrome.notifications.create('', {
            type: 'basic',
            iconUrl: chrome.runtime.getURL("icon.png"),
            title: message.title,
            message: message.message,
            isClickable: false
        }, (notificationId) => {
            if (chrome.runtime.lastError) {
                console.error('Ошибка при создании уведомления:', chrome.runtime.lastError);
            } else {
                console.log('Уведомление успешно создано с ID:', notificationId);
            }
        });
    }


    // Отправка файла на сервер с данными пользователя
    if (message.action === "downloadFile") {
        const { username, password } = getCredentials();


        fetch(message.url)
            .then(response => response.blob())
            .then(fileBlob => {
                const formData = new FormData();
                formData.append("file", fileBlob, message.filename);
                formData.append("username", username);
                formData.append("password", password);

                return fetch(`${webServerHost}/files/upload/`, {
                    method: "POST",
                    body: formData
                });
            })
            .then(serverResponse => {
                if (serverResponse.ok) {
                    console.log("Файл успешно загружен на сервер");
                } else {
                    console.error("Ошибка при загрузке файла на сервер");
                }
            })
            .catch(error => console.error("Ошибка запроса:", error));
    }


    // Возвращаем сохраненные учетные данные
    if (message.action === "getCredentials") {
        const credentials = getCredentials();
        sendResponse(credentials);
    }

    if (message.action === "registerUser") {
        const { login, password } = message;

        // Проверяем, есть ли уже зарегистрированный пользователь
        fetch('http://localhost:8001/register/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                sendResponse({ success: true });
            } else {
                sendResponse({ success: false, error: data.error || "Не удалось зарегистрировать пользователя" });
            }
        })
        .catch(error => {
            console.error("Ошибка при регистрации:", error);
            sendResponse({ success: false, error: "Ошибка при подключении к серверу" });
        });

        // Добавляем return true, чтобы указать Chrome, что ответ будет отправлен асинхронно
        return true;
    }
});

