from django.conf.urls.defaults import patterns, include, url
from .views import *
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # admin
    #url(r'^admin/', include(admin.site.urls)),

    # staff app
    url(r'^select_table/', login_required(select_table_view), name='select_table'),
    url(r'^select_columns/', login_required(select_columns_view), name='select_columns'),
    url(r'^download_trigger/', login_required(download_trigger_view), name='download_trigger'),
    url(r'^download_file/(?P<download_id>.*)$', login_required(download_file_view), name='download_file'),
    url(r'^archive/', login_required(archive_view), name='archive'),
    url(r'^dump_sql/', login_required(dump_sql_view), name='dump_sql'),
    url(r'^download_mysql_db/', login_required(Download_Mysql_View), name='download_mysql'),
    url(r'^', login_required(select_table_view), name='default'),

    # services
    #url(r'^download_analysis_db/', login_required(Download_Analysis_View), name='download_lite_db'),

    #url(r'^mp_map_download/', login_required(mp_map_download_view), name='mp_map_download'),  <<< abstract this now... any set of columns can be downloaded
    #<a href={% url "myloader:mp_map_download" %}>Download mastering physics ID map from survey</a> 
)

