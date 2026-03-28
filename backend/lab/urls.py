from django.urls import path
from .views import ExtractionMethodDetailView, ExtractionMethodListView, FormUploadView

urlpatterns = [
    path('methods/', ExtractionMethodListView.as_view(), name='lab-extraction-methods'),
    path('methods/<slug:slug>/', ExtractionMethodDetailView.as_view(), name='lab-extraction-method-detail'),
    path('upload/', FormUploadView.as_view(), name='lab-form-upload'),
]
