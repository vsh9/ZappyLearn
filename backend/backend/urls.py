"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# ZappyLearn_backend/urls.py (main project urls)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app1.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# app1/urls.py (app urls)
from django.urls import path
from app1.views import (
    GenerateWorksheetView,
    GeneratePDFView,
    WorksheetDetailView,
    HealthCheckView
)

app_name = 'app1'

urlpatterns = [
    path('generate-worksheet/', GenerateWorksheetView.as_view(), name='generate_worksheet'),
    path('generate-pdf/', GeneratePDFView.as_view(), name='generate_pdf'),
    path('worksheet/<uuid:worksheet_id>/', WorksheetDetailView.as_view(), name='worksheet_detail'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
