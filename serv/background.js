
chrome.webNavigation.onCompleted.addListener((details) => {
  
  const url = details.url;

  // Шаблон для страницы с "action=view"
  const viewPattern = /https:\/\/online-edu\.mirea\.ru\/mod\/assign\/view\.php.*action=view.*/;

  let message = null;

  if (viewPattern.test(url)) {
    console.log("Страница соответствует шаблону 'action=view'");
    message = { action: "viewPage" };
  }

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
  url: [{ hostContains: "online-edu.mirea.ru" }]
});



chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "getCookies") {
    // Обработчик для получения cookies
    chrome.cookies.getAll({ domain: "online-edu.mirea.ru" }, (cookies) => {
      const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join("; ");
      sendResponse(cookieString);
    });
    return true; 
  }


  
  if (message.action === "downloadFile") {
    // Обработчик для загрузки файла
    chrome.downloads.download({
      url: message.url,
      filename: message.filename,
      saveAs: false
    });
  }


  
  if (message.action === "showNotification") {
    // Показ уведомления
    chrome.notifications.create('', {
      type: 'basic',
      iconUrl: chrome.runtime.getURL("icon.png"),  // Убедитесь, что файл icon.png существует
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


});

