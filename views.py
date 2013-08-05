from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, render, redirect
from django.conf import settings
from mynav.nav import main_nav, tasks_nav
from .steps import steps_nav
from mypump.csvfile import CsvFile, MapFile
from .models import *
from .forms import ( 
    Select_Table_Form, 
    Select_Columns_Form,
    Download_File_Form,
    Archive_Form,
)
# mydataX imports
from django.utils.importlib import import_module
mydata = import_module(settings.MYDATA)
Source1 = mydata.models.Source1
myutils = import_module(settings.MYDATA + '.utils')
configure_source_data = myutils.configure_source_data

# Create your views here.

def select_table_view(request):

    download = task_object(request)
    # handle form (if submitted)
    if request.method == 'POST':
        form = Select_Table_Form(
            data=request.POST, 
            #db_table_choices=download.table_choices(),
        )
        if form.is_valid():
            download.table = form.cleaned_data['db_table']
            download.save()
            # Do valid form stuff here
            #return redirect('myexporter:select_table')
    else:
        #  
        form = Select_Table_Form(
            #db_table_choices=download.table_choices(),
            initial={
                # request.user.get_pref('sample_name')
                #'db_table' : download.table_choice('pref#')
                'db_table' : download.mytable_id()
            }
        )

    return render(request, 'myexporter/select_table.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'select_table'),
        "active_download_table": download.mytable_name(),
        "form": form,
    })


def select_columns_view(request):

    download = task_object(request)
    if download.table is None:
        return redirect('myexporter:select_table') 

    # handle form (if submitted)
    if request.method == 'POST':
        form = Select_Columns_Form(
            #column_choices = Download_Column.column_choices(download.id),
            column_choices = download.column_choices(),
            data=request.POST, 
        )
        if form.is_valid():
            # Do valid form stuff here
            if form.cleaned_data["columns"] != None:  
                cols = form.cleaned_data["columns"]
                Download_Column.objects.all().filter(download=download).delete()
                for cc in cols:
                    Download_Column(download=download, column_name=cc).save()
            if form.cleaned_data["seperator"] != None:
                download.seperator = form.cleaned_data['seperator']
                download.save()
            #return redirect('myexporter:select_table')
    else:
        form = Select_Columns_Form(
            #column_choices = Download_Column.column_choices(download.id),
            column_choices = download.column_choices(),
            initial={
                'seperator' : download.myseperator(),
                'columns' : Download_Column.column_choices(download.id)
            }
        )

    return render(request, 'myexporter/select_columns.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'select_columns'),
        "active_seperator": download.myseperator(),
        "active_columns": download.mycolumns(),
        "form": form,
    })

def download_file_view(request):

    download = task_object(request)

    # handle form (if submitted)
    if request.method == 'POST':
        form = Download_File_Form(
            data=request.POST, 
        )
        if form.is_valid():
            # Do valid form stuff here
            form.save_data(download)
            return redirect('myexporter:select_table')
    else:
        form = Download_File_Form(
            initial={
                'seperator' : download.myseperator(),
                'columns' : Download_Column.column_choices(download.id)
            }
        )

    return render(request, 'myexporter/download_file.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'download_file'),
        "form": form,
    })

def archive_view(request):

    download = task_object(request)

    # handle form (if submitted)
    if request.method == 'POST':
        form = Archive_Form(
            request=request,
            data=request.POST, 
        )
        if form.is_valid():
            # Do valid form stuff here
            form.save_data(download)
            return redirect('myexporter:select_table')
    else:
        form = Archive_Form(
            request=request,
        )

    return render(request, 'myexporter/archive.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'archive'),
        "form": form,
    })

def task_object(request):

    Download_Table.populate() # called way more often than necessary...
    profile = request.user.get_profile()
    prefs = profile.prefs

    # pull the users stuff
    try:
        download = Download.objects.get(pk=prefs["download_pk"])
    except:  
        download = Download(user=request.user)
        download.save()
        prefs['download_pk'] = download.id
        profile.prefs = prefs
        profile.save()

    # dig path out of settings
    Download_File.populate('/path/to/files') # called way more often than necessary too!

    return download

