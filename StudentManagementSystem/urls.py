"""Serialisers URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from UserStudentApp import views
from rest_framework.authtoken.views import obtain_auth_token as token_login
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

StudentViewSet = views.StudentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
CourseViewSet = views.CourseViewSet.as_view({
    'get': 'retrieve'
})
UserViewSet = views.UserViewSet.as_view({
    'get': 'retrieve'
})
ImagesViewSet = views.ImageViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('student/<str:pk>', StudentViewSet, name='student-detail'),
    path('user/<str:pk>', UserViewSet, name='customuser-detail'),
    path('courses/<str:pk>', CourseViewSet, name='course-detail'),
    path('images/<str:pk>', ImagesViewSet, name='image-detail'),
    path('', include('UserStudentApp.urls')),
    path('auth/', include('rest_framework.urls')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/', token_login, name='token_login'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset_password/', views.PasswordResetView.as_view(), name='reset_password'),
    path('reset/<uidb64>/<token>', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
