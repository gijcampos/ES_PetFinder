from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pets, name='listar_pets'),
    path('cadastrar/', views.cadastrar_pets, name='cadastrar_pets'),
    path('editar/<str:id>/', views.editar_pets, name='editar_pets'),
    path('excluir/<str:id>/', views.excluir_pets, name='excluir_pets'),
    path('<str:id_coleira>/historico/', views.historico_localizacao, name='historico_localizacao'),
    path('inicio/<int:id_tutor>/', views.tela_inicial_tutor, name='tela_inicial_tutor'),
    path('api/localizacao/<str:id_coleira>/', views.api_localizacao_tempo_real, name='api_localizacao_tempo_real'),
]