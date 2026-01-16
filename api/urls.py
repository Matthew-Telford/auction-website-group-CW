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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

from .views import (
    main_spa,
    user_login,
    user_signup,
    get_user_profile,
    update_user_profile,
    upload_profile_picture,
    delete_profile_picture,
    get_paginated_items,
    get_item_by_id,
    create_item,
    update_item,
    delete_item,
    get_user_items,
    create_bid,
    delete_bid,
    get_user_bids,
    get_item_bids,
    get_user_bidded_items,
    create_message,
    get_item_messages,
    update_message,
    delete_message,
)

urlpatterns = [
    path('', main_spa),
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('profile/', get_user_profile, name='user_profile'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
    path('profile/picture/upload/', upload_profile_picture, name='upload_profile_picture'),
    path('profile/picture/delete/', delete_profile_picture, name='delete_profile_picture'),
    path('items/', get_paginated_items, name='get_items'),
    path('items/create/', create_item, name='create_item'),
    path('items/<int:item_id>/', get_item_by_id, name='get_item_by_id'),
    path('items/<int:item_id>/update/', update_item, name='update_item'),
    path('items/<int:item_id>/delete/', delete_item, name='delete_item'),
    path('users/<int:user_id>/items/', get_user_items, name='get_user_items'),
    path('users/me/items/', get_user_items, name='get_my_items'),
    path('bids/create/', create_bid, name='create_bid'),
    path('bids/<int:bid_id>/delete/', delete_bid, name='delete_bid'),
    path('users/<int:user_id>/bids/', get_user_bids, name='get_user_bids'),
    path('users/me/bids/', get_user_bids, name='get_my_bids'),
    path('items/<int:item_id>/bids/', get_item_bids, name='get_item_bids'),
    path('users/<int:user_id>/bidded-items/', get_user_bidded_items, name='get_user_bidded_items'),
    path('users/me/bidded-items/', get_user_bidded_items, name='get_my_bidded_items'),
    path('messages/create/', create_message, name='create_message'),
    path('items/<int:item_id>/messages/', get_item_messages, name='get_item_messages'),
    path('messages/<int:message_id>/update/', update_message, name='update_message'),
    path('messages/<int:message_id>/delete/', delete_message, name='delete_message'),
]
