import time
import requests
from django.core.management.base import BaseCommand
from file_upload_app.models import UploadedFile
from django.conf import settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/"


def get_updates(offset=None):
    """Функция для получения обновлений от Telegram."""

    url = TELEGRAM_API_URL + "getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()


def send_message(chat_id, text):
    """Функция для отправки сообщения пользователю."""

    url = TELEGRAM_API_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


def handle_update(update):
    """Функция для обработки каждого обновления."""

    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text")

    # Пример обработки команды "/start"
    if text == "/start":
        send_message(chat_id, "Добро пожаловать в бота!")
    elif text == "/files":
        # Пример ответа списком файлов из базы данных
        files = UploadedFile.objects.all()
        if files.exists():
            file_list = "\n".join([file.file_name for file in files])
            send_message(chat_id, f"Список доступных файлов:\n{file_list}")
        else:
            send_message(chat_id, "Нет доступных файлов.")
    else:
        send_message(chat_id, "Я не понимаю эту команду.")


class Command(BaseCommand):
    help = "Запуск бота Telegram с использованием long polling"

    def handle(self, *args, **kwargs):
        self.stdout.write("Бот запущен...")
        offset = None
        while True:
            try:
                updates = get_updates(offset)
                for update in updates.get("result", []):
                    handle_update(update)
                    offset = update["update_id"] + 1  # Устанавливаем следующий offset

                time.sleep(1)  # Делаем паузу для снижения нагрузки
            except Exception as e:
                self.stderr.write(f"Ошибка: {e}")
                time.sleep(5)  # Ожидание перед повторной попыткой при ошибке

