from django.contrib.auth.models import User
from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploaded_files/')
    file_name = models.CharField(max_length=255)
    work_title = models.CharField(max_length=255)
    subj_name = models.CharField(max_length=255)


    def __str__(self):
        return self.file_name


class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=50, unique=True)
    is_logged_in = models.BooleanField(default=False)

    def __str__(self):
        return f"Session for {self.user.username}"
