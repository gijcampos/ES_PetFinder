from django.urls import path
from . import views

urlpatterns = [
    path('novo/', views.criar_agendamento, name='criar_agendamento'),
    path('cancelar/<int:id_agendamento>/', views.cancelar_agendamento, name='cancelar_agendamento'),
]