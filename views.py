from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render_to_response, render, redirect
from django.conf import settings
from datetime import datetime
from mynav.nav import main_nav, tasks_nav
from mypump.csvfile import CsvFile, MapFile
from .steps import steps_nav
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

@staff_member_required
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

@staff_member_required
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
            if form.cleaned_data["download_name"] != None:
                download.name = form.cleaned_data['download_name']
            download.save()
    else:
        form = Select_Columns_Form(
            column_choices = download.column_choices(),
            initial={
                'download_name' : download.name,
                'seperator' : download.myseperator(),
                'columns' : [ii.column_name for ii in download.download_column_set.all()]
            }
        )

    return render(request, 'myexporter/select_columns.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'select_columns'),
        "active_name": download.name,
        "active_seperator": download.myseperator(),
        "active_columns": [str(ii.column_name) for ii in download.download_column_set.all()],
        "form": form,
    })

@staff_member_required
def download_trigger_view(request):
    import csv
    from django.db import connections, router
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
            download.created = datetime.now()
            download.file_name = download.diskname() + ".csv"
            download.downloaded = True
            download.save()
            # create the file
            cols = [ii.column_name for ii in download.download_column_set.all()]
            table = []
            # check the routers for their answer on the db
            db = router.db_for_read(eval(download.table))
            cursor = connections[db].cursor()
            col_str = '`, `'.join([str(x) for x in cols]) 
            students = Source1.objects.all().order_by('id').values_list('user_id')
            if str(download.table) == 'Common1':
                where_str = " where user_id='" + "' or user_id='".join([str(x[0]) for x in students]) + "'"
            else:
                where_str = ""
            query = "select `" + col_str + "` from " + eval(download.table)._meta.db_table + where_str
            res = cursor.execute(query)
            done = cursor.fetchall() 
            for row in done:
                data = []
                for val in row:
                    if isinstance(val, unicode):
                        val = val.encode("ascii", "ignore") 
                    if isinstance(val, datetime):
                        val = val.strftime('%s')
                    try:
                        val = val.replace(',','')
                    except:
                        pass
                    data.append(val)
                table.append(data)
            # write the file
            file_path = settings.DIR_DOWNLOAD_DATA + "exports/" + download.file_name
            with open(file_path, 'wb') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=str(download.seperator), quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csvwriter.writerow(cols)
                for ii in table:
                    csvwriter.writerow(ii)
            # redirect to archive which redirects download the first time
            #new_task(request.user) 
            return redirect('myexporter:archive')
    else:
        form = Download_File_Form(
            initial={
            }
        )
    return render(request, 'myexporter/download_file.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'download_trigger'),
        "active_name": download.diskname(),
        "form": form,
    })

@staff_member_required
def archive_view(request):
    # auto download once, if fail then set to downloaded and redirect back
    download = task_object(request.user)
    all_downs = Download.objects.all().exclude(downloaded=False).order_by('-id')
    downloads = [] 
    for dd in all_downs:
        if len(dd.file_name) > 0:
            downloads.append(dd) 
    archive_list = []
    for dd in downloads:
        archive_list.append([dd.diskname, dd.id])
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
        "active_download": download.diskname(),
        "archive_list": archive_list,
        "form": form,
    })

@staff_member_required
def download_file_view(request, **kwargs):
    # if not admin don't do it
    staffmember = request.user.is_staff
    if not staffmember:
        return redirect('myexporter:download_trigger')
    if kwargs['download_id'] != '':
        download_id = kwargs['download_id']
    try:        
        download = Download.objects.get(id=download_id)
        file_path = settings.DIR_DOWNLOAD_DATA + "exports/" + download.file_name
        fsock = open(file_path,"rb")
        response = HttpResponse(fsock, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + download.file_name            
    except IOError:
        #response = HttpResponseNotFound("error downloading csv file")
        return redirect('myexporter:archive')

    # send the results
    return response

def task_object(user):
    profile = user.get_profile()
    prefs = profile.prefs
    # pull the users stuff
    try:
        # try and look it up
        download = Download.objects.get(pk=prefs["download_pk"])
        # make sure it's not 'used'
        if download.downloaded:
            download = new_task(user)
    except:  
        download = new_task(user)
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
    return download

@staff_member_required
def dump_sql_view(request):
    return render(request, 'myexporter/mysql.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'data_exporter'),
        "steps_nav": steps_nav(request.user, 'dump_sql'),
    })

@staff_member_required
def Download_Mysql_View(request):
    import os, time
    # if not admin don't do it
    staffmember = request.user.is_staff
    if not staffmember:
        return redirect('/')

    # send the results
    try:
        now = time.strftime('%Y-%m-%d-%H-%M-%S')         
        file_name = settings.DB_NAME + "_" + now + ".sql"
        file_path = settings.DIR_DOWNLOAD_DATA + "mysql/" + file_name
        
        os.system("mysqldump -u ecoach -pecoach " + settings.DB_NAME + " > " + file_path)

        fsock = open(file_path,"rb")
        response = HttpResponse(fsock, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = HttpResponseNotFound("error creating backup database file")

    return response

@staff_member_required
def Download_Common_Db_View(request):
    import os, time
    # if not admin don't do it
    staffmember = request.user.is_staff
    if not staffmember:
        return redirect('/')

    # send the results
    try:
        now = time.strftime('%Y-%m-%d-%H-%M-%S')         
        file_name = "common_" + now + ".sql"
        file_path = settings.DIR_DOWNLOAD_DATA + "mysql/" + file_name
        
        os.system("mysqldump -u ecoach -pecoach common1" + " > " + file_path)

        fsock = open(file_path,"rb")
        response = HttpResponse(fsock, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + file_name            
    except IOError:
        response = HttpResponseNotFound("error creating backup database file")

    return response


