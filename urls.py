
import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/',  include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        # Static content
        (r'^static/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(settings.FILEROOT, "static")}),
    )

urlpatterns += patterns('',
    # Main app
    (r'^', include('lastgui.urls')),
)
