from django.contrib import admin
from .models import UploadedFile, UserSession

admin.site.register(UploadedFile)
admin.site.register(UserSession)

