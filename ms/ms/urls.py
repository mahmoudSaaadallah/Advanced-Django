# This is your main PROJECT urls.py file

from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Your app's API URLs
    path('api/', include('trader.urls')), 
]


if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
    
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]