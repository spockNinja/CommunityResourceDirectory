from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
    path('submit/success/', views.submit_success, name='submit_success'),
]
