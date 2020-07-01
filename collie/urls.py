"""collie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.documentation import include_docs_urls

API_TITLE = 'Collie API'
API_DESCRIPTION = 'A Web API Reference for Collie.'


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api/portal/', include('portal.urls')),
    url(r'^api/', include('website.urls')),
    url(r'^api/event/', include('event.urls')),
    url(r'^api/report/', include('report.urls')),
    url(r'^api/configure/', include('configure.urls')),
    url(r'^api/dashboard/', include('dashboard.urls')),
    url(r'^api/docs/', include_docs_urls(title=API_TITLE,
                                        description=API_DESCRIPTION,
                                        permission_classes=[]))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
