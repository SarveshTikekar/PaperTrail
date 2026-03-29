from django.urls import path
from .views import (
    ExtractionMethodDetailView, ExtractionMethodListView, FormUploadView, 
    OCRTestView, ExtractionRecordListView, ExtractionRecordDetailView
)

urlpatterns = [
    path('methods/', ExtractionMethodListView.as_view(), name='lab-extraction-methods'),
    path('methods/<slug:slug>/', ExtractionMethodDetailView.as_view(), name='lab-extraction-method-detail'),
    path('ocr-test/', OCRTestView.as_view(), name='lab-ocr-test'),
    path('upload/', FormUploadView.as_view(), name='lab-form-upload'),
    path('records/', ExtractionRecordListView.as_view(), name='lab-extraction-records'),
    path('records/<str:record_id>/', ExtractionRecordDetailView.as_view(), name='lab-extraction-record-detail'),
]
