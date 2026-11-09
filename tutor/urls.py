from django.urls import path
from . import views

app_name = 'tutor'  # Ajuda no namespace das URLs em templates e redirecionamentos

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('editar/<int:id>/', views.editar_perfil, name='editar_perfil'),
    path('excluir/<int:id>/', views.excluir_perfil, name='excluir_perfil'),
]