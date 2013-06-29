from django import forms
from django.conf import settings
from .models import Download
from datetime import datetime
from django.utils.importlib import import_module
mydata = import_module(settings.MYDATA)
Source1 = mydata.models.Source1

class Select_Table_Form(forms.Form):

    def __init__(self, request, *args, **kwargs):
        super(Select_Table_Form, self).__init__(*args, **kwargs)

    def save_data(self, download):
        download.save()


class Select_Columns_Form(forms.Form):
    pass

class Download_File_Form(forms.Form):
    pass

class Archive_Form(forms.Form):
    pass
