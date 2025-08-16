from django.urls import path
from . import views # Import the views.py file from this app

urlpatterns = [
    # When a user visits the homepage (''), run the 'home' view function
    path('', views.home, name='home'),
]