
from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('login', login),
    path('signup', register),
    path('logout', logout),
    path('products', products_get),
    path('cart', cart_get),
    path('cart/<int:pk>', cart_post_delete),
    path('order', order_get_post),
    path('product', admin_get_post),
]
