
from django.urls import path, include
from .views import *

urlpatterns = [
    path('product', productcreate),
    path('products', productview),
    path('product/<int:pk>', productcrud),
    path('cart/', cartview),
    path('cart/<int:pk>', cartedit),
    path('order', orderview)
]