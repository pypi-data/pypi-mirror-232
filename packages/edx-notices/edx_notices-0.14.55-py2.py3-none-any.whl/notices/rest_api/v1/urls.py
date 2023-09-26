"""v1 API URLS"""
from django.urls import path

from notices.rest_api.v1 import views


urlpatterns = [
    path("unacknowledged", views.ListUnacknowledgedNotices.as_view(), name="unacknowledged_notices"),
    path("acknowledge", views.AcknowledgeNotice.as_view(), name="acknowledge_notice"),
]
