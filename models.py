from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Download(models.Model):
    # [12m Download_Column__download]
    user = models.ForeignKey(User, to_field='username') 
    created = models.DateTimeField(auto_now=False,blank=True, null=True)
    table = models.CharField(max_length=100)
    file_name = models.CharField(max_length=100)

class Download_Column(models.Model):
    column_name = models.CharField(max_length=100)
    download = models.ForeignKey(Download)


