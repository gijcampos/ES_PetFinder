from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/<int:id_tutor>/', views.cadastro, name='cadastro_emergencia'),
]