from django.urls import path
from . import views

urlpatterns = [
    path('',views.getAlProperties,name='flats'),
]