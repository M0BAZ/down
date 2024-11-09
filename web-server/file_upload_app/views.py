from django.views.decorators.csrf import csrf_exempt
from .models import UploadedFile
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate
from file_upload_app.models import UserSession


def create_user_session(username, telegram_id):
    try:
        # Найдем пользователя по его имени (или другим уникальным полям)
        user = User.objects.get(username=username)

        # Создадим или получим сессию для этого пользователя
        user_session, created = UserSession.objects.get_or_create(user=user, telegram_id=telegram_id)

        if created:
            print(f"Session created for {user.username} with Telegram ID {telegram_id}")
        else:
            print(f"Session already exists for {user.username}")

        return user_session
    except User.DoesNotExist:
        print(f"User with username '{username}' does not exist")
        return None


def get_file_list(request):
    files = UploadedFile.objects.all()
    file_data = [{"name": file.file_name, "url": file.file.url} for file in files]
    return JsonResponse(file_data, safe=False)

@method_decorator(csrf_exempt, name='dispatch')
class UploadFileView(View):
    def post(self, request):
        if request.FILES.get('file'):
            file = request.FILES['file']
            work_title = request.POST.get('work_title', '')
            subj_name = request.POST.get("subj_name", '')

            uploaded_file = UploadedFile.objects.create(
                file=file,
                file_name=file.name,
                work_title=work_title,
                subj_name=subj_name
            )
            return JsonResponse({'status': 'success', 'file_id': uploaded_file.id})
        return JsonResponse({'status': 'failed'}, status=400)


@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            login = data.get('login')
            password = data.get('password')

            if User.objects.filter(username=login).exists():
                return JsonResponse({'success': False, 'message': 'Пользователь уже существует'})

            # Создаем нового пользователя
            user = User.objects.create_user(username=login, password=password)
            return JsonResponse({'success': True, 'message': 'Пользователь успешно зарегистрирован'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'})
    else:
        return JsonResponse({'success': False, 'message': 'Метод не разрешен'})


@csrf_exempt
def check_user_credentials(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        login = data.get('login')
        password = data.get('password')

        user = authenticate(username=login, password=password)
        if user is not None:
            return JsonResponse({'success': True, 'message': 'Авторизация успешна'})
        else:
            return JsonResponse({'success': False, 'message': 'Неверные логин или пароль'})
    return JsonResponse({'success': False, 'message': 'Метод не разрешен'})