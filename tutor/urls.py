from django.urls import path
from . import views

app_name = 'tutor'  # Ajuda no namespace das URLs em templates e redirecionamentos

urlpatterns = [
    # Exemplo de rota inicial para a view index/home do tutor:
    # path('', views.index, name='index'),
]