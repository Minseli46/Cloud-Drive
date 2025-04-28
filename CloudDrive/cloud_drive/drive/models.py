from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_folder = models.ForeignKey('self', null=True, blank=True, related_name='subfolders', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class File(models.Model):
    file = models.FileField(upload_to='user_files/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, null=True, blank=True, related_name='files', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)  # Permettre null temporairement
    file_type = models.CharField(max_length=50, null=True, blank=True)  # Permettre null temporairement

    def __str__(self):
        return self.file.name
