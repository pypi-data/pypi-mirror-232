from django.urls import path, include
from rest_framework import routers

from kfsd.apps.endpoints.views.requests.endpoint import EndpointModelViewSet

router = routers.DefaultRouter()
router.include_format_suffixes = False

router.register("requests/endpoint", EndpointModelViewSet, basename="endpoint")

urlpatterns = [
    path("", include(router.urls)),
]
