# app1/urls.py
from django.urls import path
from .views import (
    GenerateWorksheetView,
    GeneratePDFView,
    WorksheetDetailView,
    HealthCheckView
)

urlpatterns = [
    path('generate-worksheet/', GenerateWorksheetView.as_view(), name='generate_worksheet'),
    path('generate-pdf/', GeneratePDFView.as_view(), name='generate_pdf'),
    path('worksheet/<uuid:worksheet_id>/', WorksheetDetailView.as_view(), name='worksheet_detail'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
