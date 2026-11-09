from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/<int:id_tutor>/', views.cadastro, name='cadastro_emergencia'),
    path('editar/<int:id_contato>/', views.editar, name='editar_emergencia'),
    path('excluir/<int:id_contato>/', views.excluir, name='excluir_emergencia'),
]