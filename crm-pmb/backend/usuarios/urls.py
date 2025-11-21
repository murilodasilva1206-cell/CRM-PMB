"""
URLs do módulo Usuarios
"""
from django.urls import path
from .views import user_me

urlpatterns = [
    path('me/', user_me, name='user-me'),
]
