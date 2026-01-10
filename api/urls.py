"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

from .views import (
    main_spa,
    user_login,
    get_user_profile,
    upload_profile_picture,
    delete_profile_picture,
)

urlpatterns = [
    path('', main_spa),
    path('login/', user_login, name='login'),
    path('profile/', get_user_profile, name='user_profile'),
    path('profile/picture/upload/', upload_profile_picture, name='upload_profile_picture'),
    path('profile/picture/delete/', delete_profile_picture, name='delete_profile_picture'),
]
