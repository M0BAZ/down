import time
import requests
from django.core.management.base import BaseCommand
from file_upload_app.models import UploadedFile
from django.conf import settings
from django.contrib.auth.models import User
from file_upload_app.models import UserSession

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/"

# Получение обновлений от Telegram
def get_updates(offset=None):
    url = TELEGRAM_API_URL + "getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()

# Отправка сообщений пользователю
def send_message(chat_id, text):
    url = TELEGRAM_API_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def authenticate_user(chat_id, username, password):
    """Проверка логина и пароля и создание сессии."""
    try:
        user = User.objects.get(username=username)

        # Допустим, пароли хранятся в системе Django
        if user.check_password(password):
            # Удаляем старую сессию, если она существует
            UserSession.objects.filter(telegram_id=str(chat_id)).delete()
            UserSession.objects.filter(user=user).delete()

            # Создаем новую сессию
            user_session = UserSession.objects.create(user=user, telegram_id=str(chat_id), is_logged_in=True)

            send_message(chat_id, "Вы успешно авторизованы!")
        else:
            send_message(chat_id, "Неверный пароль. Попробуйте снова.")
    except User.DoesNotExist:
        send_message(chat_id, "Пользователь с таким логином не найден.")

def handle_update(update):
    """Функция для обработки каждого обновления."""
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text")

    # Получаем данные из текста команды
    if text == "/start":
        send_message(chat_id, "Добро пожаловать! Пожалуйста, войдите, введя свой логин и пароль.")

    elif text.startswith("/login"):
        # Предполагаем, что логин и пароль передаются через пробел в сообщении
        try:
            _, username, password = text.split()
            authenticate_user(chat_id, username, password)
        except ValueError:
            send_message(chat_id, "Неверный формат команды. Используйте: /login <логин> <пароль>")

    elif text == "Сосал?":
        send_message(chat_id, "Сам сосал, у меня твой ip, логин и пароль, лох. Попробуй ещё повыкабениваться.")
    elif text == "/files":
        # Проверка, авторизован ли пользователь
        try:
            user_session = UserSession.objects.get(telegram_id=str(chat_id))

            if user_session.is_logged_in:
                # Получаем список файлов для авторизованного пользователя
                files = UploadedFile.objects.all()  # или другой запрос для ваших файлов
                if files.exists():
                    file_list = "\n".join([file.file_name for file in files])
                    send_message(chat_id, f"Список доступных файлов:\n{file_list}")
                else:
                    send_message(chat_id, "Нет доступных файлов.")
            else:
                send_message(chat_id, "Вы не авторизованы. Пожалуйста, войдите.")
        except UserSession.DoesNotExist:
            send_message(chat_id, "Вы не авторизованы. Пожалуйста, войдите.")



# Команда для запуска бота
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
