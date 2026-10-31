from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pets, name='listar_pets'),
    path('cadastrar/', views.cadastrar, name='cadastrar_pet'),
    path('editar/<int:id>/', views.editar, name='editar_pet'),
    path('excluir/<int:id>/', views.excluir, name='excluir_pet'),
]