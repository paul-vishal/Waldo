from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register/', views.register),
    path('login_page/login/', views.login),
    path('login_page/', views.login_page),
    path('login_page/login/updatePreference/', views.updatePreference),
    path('login_page/login/notifyUser/', views.notifyUser),
    path('login_page/login/advertise/', views.advertise)
]
