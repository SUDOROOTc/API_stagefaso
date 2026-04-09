from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StageViewSet

router = DefaultRouter()
router.register(r'api/stages', StageViewSet, basename='api/stage')

urlpatterns = [
    path('', include(router.urls)),
]