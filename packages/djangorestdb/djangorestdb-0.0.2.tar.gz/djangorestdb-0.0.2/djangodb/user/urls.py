
from django.urls import path, include
from .views import login, signup, Logout

urlpatterns = [
    path('login', login),
    path('signup', signup),
    path('logout', Logout.as_view())
]