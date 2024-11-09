const webServerHost = 'http://localhost:8001';

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action != "viewPage") {
        return;
    }
    console.log("Перешли на страницу с шаблоном 'action=view'");

    const table = document.querySelector('.submissionstatussubmitted.cell.c1.lastcol').textContent;
    if (table != "Отправлено для оценивания") {
        return;
    }

    const fileElement = document.querySelectorAll('.fileuploadsubmission a');
    const fileUrl = fileElement[fileElement.length - 1].getAttribute("href");

    // Проверяем, выполнен ли вход в плагин, запрашивая учетные данные у background.js
    chrome.storage.local.get(['username', 'password'], (credentials) => {
        if (!credentials.username || !credentials.password) {
            chrome.runtime.sendMessage({
                action: "showNotification",
                title: "Вход не выполнен",
                message: "Пожалуйста, выполните вход в плагин для загрузки файла на сервер."
            });
            return;
        }


        chrome.runtime.sendMessage({action: "getCookies"}, async (cookieString) => {
            // Загружаем файл с заголовками и cookies
            const response = await fetch(fileUrl, {
                method: "GET",
                headers: {
                    "Cookie": cookieString
                }
            });

            const fileBlob = await response.blob();


            const fileElement_2 = document.querySelectorAll(".fileuploadsubmission img");
            const fileName = fileElement_2[fileElement_2.length - 1].getAttribute("title");

            const workTitle = document.querySelector(".page-header-headings h1").textContent;

            const subjName = document.querySelectorAll(".breadcrumb-item a")[1].textContent;


            // Создание FormData для отправки файла на сервер
            const formData = new FormData();
            formData.append("file", fileBlob, fileName);
            formData.append("work_title", workTitle);  // Передача названия работы
            formData.append("subj_name", subjName);
            formData.append("username", credentials.username);
            formData.append("password", credentials.password);

            // Отправка запроса на сервер Django
            fetch(`${webServerHost}/files/upload/`, {
                method: "POST",
                body: formData
            })
                .then(serverResponse => {
                    if (serverResponse.ok) {
                        console.log("Файл и название работы успешно загружены на сервер");
                        chrome.runtime.sendMessage({
                            action: "showNotification",
                            title: "Файл загружен",
                            message: `Файл ${fileName} успешно загружен на сервер.`
                        });

                    } else {
                        console.error("Ошибка при загрузке файла на сервер");
                    }
                })
                .catch(error => console.error("Ошибка запроса:", error));
        });
    });

    sendResponse({status: "Сообщение обработано в content.js"});
});

