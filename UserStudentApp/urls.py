from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'student', views.StudentViewSet, basename='students-view')
router.register(r'user', views.UserViewSet, basename='users-view')
router.register(r'course', views.CourseViewSet, basename='courses-view')
router.register(r'images', views.ImageViewSet, basename='images-view')

user_view = views.UserViewSet.as_view({'get':'retrieve'})
# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
