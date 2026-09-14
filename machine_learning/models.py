from django.db import models

# Create your models here.

class MachineLearningModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class UserInfo(models.Model):    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    text_area = models.TextField()
    file_field = models.FileField(upload_to='uploads/')
    checkbox = models.BooleanField(default=False)

    def __str__(self):
     return f"{self.first_name} {self.last_name}"