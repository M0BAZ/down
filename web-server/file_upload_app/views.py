from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedFile
from django.views import View
from django.utils.decorators import method_decorator


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

