from django.db import models

# Create your models here.
from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploaded_files/')
    file_name = models.CharField(max_length=255)
    work_title = models.CharField(max_length=255)
    subj_name = models.CharField(max_length=255)

    def __str__(self):
        return self.file_name
