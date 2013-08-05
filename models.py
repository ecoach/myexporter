from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.conf import settings
from mylogger.models import ELog
mydata = import_module(settings.MYDATA)
Source1 = mydata.models.Source1

# Create your models here.

class Download_Table(models.Model):
    # [12m Download_Table__Download]
    table_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)

    def __unicode__(self):
        #return str(self.id) + '_' + self.table_name
        return self.table_name

    def disk_name(self):
        return self.__unicode__()

    @classmethod
    def populate(self):
        # These should be models available
        available = [
            ['Event Log', 'ELog'],
            ['MTS Source', 'Source1']
        ]
        # If models not found, create them 
        for aa in available:
            on_file = Download_Table.objects.filter(table_name=aa[0], model_name=aa[1]) 
            if len(on_file) < 1:
                dd = Download_Table(table_name=aa[0], model_name=aa[1])
                dd.save()

class Download_File(models.Model):
    # [12m Download_Table__Download]
    path = models.CharField(max_length=200)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        #return str(self.id) + '_' + self.table_name
        return str(self.id) + self.name

    def disk_name(self):
        return self.__unicode__()

    @classmethod
    def populate(self, path):
        # Look on disk to find all csv files at path
        return
        available = [['path'], ['name']]
        # If models not found, create them 
        for aa in available:
            on_file = Download_File.objects.filter(path=aa[0], name=aa[1]) 
            if len(on_file) < 1:
                dd = Download_Table(table_name=aa[0], model_name=aa[1])
                dd.save()


class Download(models.Model):
    user = models.ForeignKey(User, to_field='username') 
    table = models.ForeignKey(Download_Table, null=True) 
    # [12m Download__Download_Column]
    seperator = models.CharField(max_length=10, null=True)
    file_name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now=False,blank=True, null=True)

    def mytable_id(self):
        if not self.table is None:
            return self.table.id
        else:
            return 1

    def mytable_name(self):
        if not self.table is None:
            return self.table.table_name
        else:
            return ''

    def myseperator(self):
        if not self.seperator is None:
            return self.seperator
        else:
            return ''

    def mycolumns(self):
        cols = Download_Column.column_choices(self.id)
        if len(cols) > 0: 
            return map(str, cols)
        else:
            return ''

    def column_choices(self):
        ids = []
        for ff in eval(self.table.model_name)._meta.fields:
            ids.append(ff.name)
        return zip(ids, ids)
        #return zip([1,2], ['hi', 'yo'])

class Download_Column(models.Model):
    column_name = models.CharField(max_length=100)
    download = models.ForeignKey(Download)

    @classmethod
    def column_choices(self, download_id):
        #return [1]
        try:
            cols = Download_Column.objects.all().filter(download=download_id).values_list('column_name')
            return [x[0] for x in cols]
        except:
            return []


"""
def table_choices(self):
    db_table_choices = [('1', 'table1'), ('2', 'table2')]
    return db_table_choices

def table_choice(self, pref):
    table_selection = 1
    for cc in self.table_choices():
        if cc[1] == pref:
            table_selection = cc[0]
    return table_selection
"""


