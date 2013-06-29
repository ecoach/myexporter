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
 
    # handle form (if submitted)
    if request.method == 'POST':
        form = Select_Table_Form(
            request=request,
            data=request.POST, 
        )
        if form.is_valid():
            # Do valid form stuff here
            form.save_data(download)
            return redirect('myexporter:select_table')
    else:
        #  
        form = Select_Table_Form(
            request=request,
        )

    return render(request, 'myexporter/select_table.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'select_table'),
        "form": form,
    })


def select_columns_view(request):
    return render(request, 'myexporter/select_columns.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'select_columns'),
        #"form": form,
    })

def download_file_view(request):
    return render(request, 'myexporter/download_file.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'download_file'),
        #"form": form,
    })

def archive_view(request):
    return render(request, 'myexporter/archive.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'archive'),
        #"form": form,
    })




