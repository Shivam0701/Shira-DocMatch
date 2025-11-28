"""
URL configuration for compare app.
"""
from django.urls import path
from .views import DocumentCompareView

urlpatterns = [
    path('compare/', DocumentCompareView.as_view(), name='compare'),
]

