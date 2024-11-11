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


# Функция для создания клавиатуры
def create_keyboard():
    return {
        "keyboard": [
            [{"text": "🔑 Войти"}, {"text": "📂 Мои файлы"}],
            [{"text": "ℹ️ О боте"}, {"text": "❓ Помощь"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }


# Отправка сообщений с опциональной клавиатурой
def send_message(chat_id, text, keyboard=None):
    url = TELEGRAM_API_URL + "sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = keyboard
    requests.post(url, json=data)


# Аутентификация пользователя
def authenticate_user(chat_id, username, password):
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            UserSession.objects.filter(telegram_id=str(chat_id)).delete()
            UserSession.objects.filter(user=user).delete()
            UserSession.objects.create(user=user, telegram_id=str(chat_id), is_logged_in=True)
            send_message(chat_id, "Вы успешно авторизованы!")
        else:
            send_message(chat_id, "Неверный пароль. Попробуйте снова.")
    except User.DoesNotExist:
        send_message(chat_id, "Пользователь с таким логином не найден.")


def send_file(chat_id, file_path):
    url = TELEGRAM_API_URL + "sendDocument"
    with open(file_path, 'rb') as file_data:
        data = {"chat_id": chat_id}
        files = {"document": file_data}
        requests.post(url, data=data, files=files)


# Обработка каждого обновления
def handle_update(update):
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text")

    print(f"Полученный текст: {text}")

    # Проверяем команду и отправляем сообщение с клавиатурой
    if text == "/start" or text == "❓ Помощь":
        send_message(chat_id, "Добро пожаловать! Воспользуйтесь командами ниже для навигации.", create_keyboard())

    elif text == "🔑 Войти":
        send_message(chat_id, "Введите команду '/login логин пароль' для авторизации.")

    elif text.startswith("/login"):
        if text.count(" ") == 2:
            try:
                _, username, password = text.split()
                authenticate_user(chat_id, username, password)
            except ValueError:
                send_message(chat_id, "Неверный формат команды. Используйте: '/login логин пароль'")
        else:
            send_message(chat_id, "Введите логин и пароль раздельно друг от друга")

    elif text == "📂 Мои файлы":
        try:
            user_session = UserSession.objects.get(telegram_id=str(chat_id))
            if user_session.is_logged_in:
                files = UploadedFile.objects.all()
                if files.exists():
                    file_list = "\n".join([file.file_name for file in files])
                    send_message(chat_id, f"Список доступных файлов:\n{file_list}")
                else:
                    send_message(chat_id, "Нет доступных файлов.")
            else:
                send_message(chat_id, "Вы не авторизованы. Пожалуйста, войдите.")
        except UserSession.DoesNotExist:
            send_message(chat_id, "Вы не авторизованы. Пожалуйста, войдите.")

    elif text == "ℹ️ О боте":
        send_message(chat_id,
                     "Этот бот помогает получать доступ к файлам. Чтобы использовать его, выполните вход с помощью команды /login.")

    elif text == "/files":
        try:
            user_session = UserSession.objects.get(telegram_id=str(chat_id))
            if user_session.is_logged_in:
                files = UploadedFile.objects.all()
                if files.exists():
                    keyboard = {
                        "inline_keyboard": [
                            [{"text": file.file_name, "callback_data": f"file_{file.id}"}] for file in files
                        ]
                    }
                    send_message(chat_id, "Выберите файл для скачивания:", keyboard)
                else:
                    send_message(chat_id, "Нет доступных файлов.")
            else:
                send_message(chat_id, "Вы не авторизованы. Пожалуйста, войдите.")
        except UserSession.DoesNotExist:
            send_message(chat_id, "Вы не авторизованы. Пожалуйста, войдите.")

    elif text.lower().startswith("file_"):
        file_id = text.split("_")[1]
        try:
            uploaded_file = UploadedFile.objects.get(id=file_id)
            # Передаем путь к файлу как строку напрямую
            file_path = uploaded_file.file.path
            with open(file_path, 'rb') as file:
                requests.post(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendDocument", data={
                    'chat_id': chat_id,
                }, files={'document': file})
        except UploadedFile.DoesNotExist:
            send_message(chat_id, "Файл не найден. Попробуйте выбрать другой файл.")
        except:
            send_message(chat_id, "Ошибка")

    elif "извини" in text.lower():
        send_message(chat_id, "Пацаны не извиняются")

    elif text.lower() == "сосал?":
        send_message(chat_id, "Сам сосал, у меня твой ip, логин и пароль, лох. Попробуй ещё повыкабениваться.")

    else:
        send_message(chat_id, "Я хз о чем ты")


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
                    offset = update["update_id"] + 1
                time.sleep(1)
            except Exception as e:
                self.stderr.write(f"Ошибка: {e}")
                time.sleep(5)
