from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.conf import settings
from mylogger.models import ELog
from myemailer.models import Message
mydata = import_module(settings.MYDATA)
Source1 = mydata.models.Source1
Common1 = mydata.models.Common1

# Create your models here.

class Download(models.Model):
    user = models.ForeignKey(User, to_field='username') 
    table = models.CharField(max_length=30, null=True)
    # [12m Download__Download_Column]
    seperator = models.CharField(max_length=10, null=True, default=',')
    name = models.CharField(max_length=100)
    file_name = models.CharField(max_length=100)
    downloaded = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=False,blank=True, null=True)

    def __unicode__(self):
        return str(self.id) + '_' + self.name

    def get_name(self):
        return self.__unicode__()

    def diskname(self):
        return str(self.id) + '_' + self.name

    def myseperator(self):
        if not self.seperator is None:
            return self.seperator
        else:
            return ''

    def column_choices(self):
        ids = []
        for ff in eval(self.table)._meta.fields:
            ids.append(ff.column)
        return zip(ids, ids)

class Download_Column(models.Model):
    column_name = models.CharField(max_length=100)
    download = models.ForeignKey(Download)



