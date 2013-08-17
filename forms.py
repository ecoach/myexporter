from django import forms
from django.conf import settings
from .models import *
from datetime import datetime
from django.utils.importlib import import_module
#mydata = import_module(settings.MYDATA)
#Source1 = mydata.models.Source1

class Select_Table_Form(forms.Form):
    db_table = forms.ChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super(Select_Table_Form, self).__init__(*args, **kwargs)
        self.fields['db_table'].choices = self.table_choices()

    def table_choices(self):
        available = [
            ('ELog', 'ELog'),
            ('Source1', 'Source1'),
            ('Common1', 'Common1')
        ]
        return available

class Select_Columns_Form(forms.Form):
    columns = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    seperator = forms.CharField(required=False, max_length=1)
    download_name = forms.CharField(required=False)

    def __init__(self, column_choices, *args, **kwargs):
        super(Select_Columns_Form, self).__init__(*args, **kwargs)
        self.fields['columns'].choices = column_choices

class Download_File_Form(forms.Form):
    pass

class Archive_Form(forms.Form):
    download = forms.ModelChoiceField(required=False, queryset=Download.objects.all().order_by('-id'))

    #def __init__(self, *args, **kwargs):
        #super(Select_Table_Form, self).__init__(*args, **kwargs)
