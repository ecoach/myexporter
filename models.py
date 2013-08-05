from django.db import models
from django.contrib.auth.models import User

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
            ['Event Log', 'Elog'],
            ['MTS Source', 'Source1']
        ]
        # If models not found, create them 
        for aa in available:
            on_file = Download_Table.objects.filter(table_name=aa[0], model_name=aa[1]) 
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

    def column_choices(self):
        return zip([1,2,4], ['hi', 'there', 'yo'])

class Download_Column(models.Model):
    column_name = models.CharField(max_length=100)
    download = models.ForeignKey(Download)

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


