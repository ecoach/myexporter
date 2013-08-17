from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, render, redirect
from django.conf import settings
from datetime import datetime
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

    download = task_object(request.user)
    # handle form (if submitted)
    if request.method == 'POST':
        form = Select_Table_Form(
            data=request.POST, 
        )
        if form.is_valid():
            download.table = form.cleaned_data['db_table']
            download.save()
            # Do valid form stuff here
            #return redirect('myexporter:select_table')
    else:
        #  
        form = Select_Table_Form(
            initial={
                'db_table' : download.table
            }
        )

    return render(request, 'myexporter/select_table.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'select_table'),
        "active_download_table": download.table,
        "form": form,
    })


def select_columns_view(request):
    download = task_object(request.user)
    if download.table is None:
        return redirect('myexporter:select_table') 
    # handle form (if submitted)
    if request.method == 'POST':
        form = Select_Columns_Form(
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
    else:
        form = Select_Columns_Form(
            column_choices = download.column_choices(),
            initial={
                'seperator' : download.myseperator(),
                'columns' : [ii.column_name for ii in download.download_column_set.all()]
            }
        )

    return render(request, 'myexporter/select_columns.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'select_columns'),
        "active_seperator": download.myseperator(),
        "active_columns": [str(ii.column_name) for ii in download.download_column_set.all()],
        "form": form,
    })

def download_trigger_view(request):
    import csv
    download = task_object(request.user)
    if download.table is None:
        return redirect('myexporter:select_table') 
    # handle form (if submitted)
    if request.method == 'POST':
        form = Download_File_Form(
            data=request.POST, 
        )
        if form.is_valid():
            # Do valid form stuff here
            download.name = form.cleaned_data['download_name']
            download.created = datetime.now()
            download.file_name = download.diskname() + ".csv"
            download.downloaded = False
            download.save()
            # create the file
            cols = [ii.column_name for ii in download.download_column_set.all()]
            res = eval(download.table).objects.values_list(*cols)
            # write the file
            file_path = settings.DIR_DOWNLOAD_DATA + "exports/" + download.file_name
            with open(file_path, 'wb') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=str(download.seperator), quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for ii in res:
                    csvwriter.writerow(ii)
            # redirect to archive which redirects download the first time
            return redirect('myexporter:archive')
    else:
        form = Download_File_Form(
            initial={
                'download_name' : download.name,
            }
        )
    return render(request, 'myexporter/download_file.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'download_trigger'),
        "active_name": download.diskname(),
        "form": form,
    })

def archive_view(request):
    # auto download once, if fail then set to downloaded and redirect back
    download = task_object(request.user)
    if not download.downloaded:
        return redirect('myexporter:download_file')
        
    # handle form (if submitted)
    if request.method == 'POST':
        form = Archive_Form(
            data=request.POST, 
        )
        if form.is_valid():
            # Copy the old digestion
            new = form.cleaned_data['download'] # still old
            cols = Download_Column.objects.filter(download=new.id) # old cols
            new.id = download.id # becomes new
            new.user = download.user # becomes new
            new.save() # save new
            Download_Column.objects.filter(download=new.id).delete() # delete existing cols
            for cc in cols:     # copy old cols
                cc.id = None    # become new
                cc.download_id = new.id
                cc.save() 
            return redirect('myexporter:archive')
    else:
        form = Archive_Form(
        )

    return render(request, 'myexporter/archive.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'archive'),
        "form": form,
    })

def download_file_view(request):
    # if not admin don't do it
    download = task_object(request.user)
    staffmember = request.user.is_staff
    if not staffmember:
        return redirect('myexporter:download_trigger')
    try:        
        file_path = settings.DIR_DOWNLOAD_DATA + "exports/" + download.file_name
        fsock = open(file_path,"rb")
        response = HttpResponse(fsock, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + download.file_name            
        download.downloaded = True
        download.save() 
        new_task(request.user) 
    except IOError:
        #response = HttpResponseNotFound("error downloading csv file")
        download.downloaded=True
        download.save()
        return redirect('myexporter:archive')

    # send the results
    return response

def task_object(user):
    profile = user.get_profile()
    prefs = profile.prefs
    # pull the users stuff
    try:
        download = Download.objects.get(pk=prefs["download_pk"])
    except:  
        download = Download(user=user)
        download.save()
        prefs['download_pk'] = download.id
        profile.prefs = prefs
        profile.save()
    return download

def new_task(user):
    profile = user.get_profile()
    prefs = profile.prefs
    # create a new download and save to user
    download = Download(user=user)
    download.save()
    prefs['download_pk'] = download.id
    profile.prefs = prefs
    profile.save()

