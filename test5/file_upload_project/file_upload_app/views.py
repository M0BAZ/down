from django.shortcuts import render

# Create your views here.
# file_upload_app/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedFile
import os

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        work_title = request.POST.get('work_title', '')  # Получаем название практической работы
        subj_name = request.POST.get("subj_name", '')

        uploaded_file = UploadedFile.objects.create(
            file=file,
            file_name=file.name,
            work_title=work_title,
            subj_name=subj_name
        )
        return JsonResponse({'status': 'success', 'file_id': uploaded_file.id})
    return JsonResponse({'status': 'failed'}, status=400)
