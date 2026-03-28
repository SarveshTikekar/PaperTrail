from django.urls import path
from .views import FormUploadView

urlpatterns = [
    path('upload/', FormUploadView.as_view(), name='lab-form-upload'),
]
