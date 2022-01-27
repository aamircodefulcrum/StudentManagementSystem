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
from django.urls import path,include
from UserStudentApp import views
from rest_framework.authtoken.views import obtain_auth_token as token_login
from django.conf import settings
from django.conf.urls.static import static


urlpatterns =  [
    path('admin/', admin.site.urls),
    path('student/<str:pk>', views.StudentViewSet.as_view({'get': 'retrieve','put': 'update','patch': 'partial_update','delete': 'destroy'}), name='student-detail'), 
    path('users/<str:pk>', views.UserViewSet.as_view({'get':'retrieve'}), name='customuser-detail'),
    path('course/<str:pk>', views.CourseViewSet.as_view({'get':'retrieve'}), name='course-detail'),
    path('images/<str:pk>', views.ImageViewSet.as_view({'get': 'retrieve','put': 'update','patch': 'partial_update','delete': 'destroy'}), name='image-detail'),
    path('', include('UserStudentApp.urls')),
    path('auth/', include('rest_framework.urls')),
    path('auth-token/', token_login, name='login'),
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)