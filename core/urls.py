from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.shortcuts import render

def error_404(request, exception=None):
    url_completa = request.build_absolute_uri()

    return render(request, 'accounts/404.html', {'url_capturada':url_completa})


urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^.*$', error_404),

]
