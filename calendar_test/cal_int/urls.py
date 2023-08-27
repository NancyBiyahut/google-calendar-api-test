# calendar_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_event/', views.add_event, name='add_event'),
    path('get_hours/<int:number_of_days>/', views.get_hours, name='get_hours'),
]
