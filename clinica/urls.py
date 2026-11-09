from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/<int:id_tutor>/', views.cadastro, name='cadastrar_clinica'),
    path('listar/<int:id_tutor>/', views.listar, name='listar_clinica'),
    path('editar/<int:id_clinica>/', views.editar, name='editar_clinica'),
    path('excluir/<int:id_clinica>/', views.excluir, name='excluir_clinica'),
]