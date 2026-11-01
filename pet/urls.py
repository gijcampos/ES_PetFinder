from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pets, name='listar_pets'),
    path('cadastrar/', views.cadastrar_pets, name='cadastrar_pets'),
    path('editar/<str:id>/', views.editar_pets, name='editar_pets'),
    path('excluir/<str:id>/', views.excluir_pets, name='excluir_pets'),
]