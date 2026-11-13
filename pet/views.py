from django.shortcuts import render, redirect, get_object_or_404
from .models import Pet, PetTutor
from .forms import PetsForm
from datetime import date, datetime, timedelta
from django.contrib import messages
from .services import obter_historico_diario

# ===== LISTAR PETS =====

def listar_pets(request):
    pets = Pet.objects.all()
    return render(request, 'pet/<listar_pets.html>', {'pets': pets})

# ===== CADASTRO DE PETS =====

def cadastrar_pets(request):
    if request.method == 'POST':
        form = PetsForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("listar_pets")

    else:
        form = PetsForm()
    return render(request, 'pet/cadastrar_pets.html', {'form': form})

# ===== EDIÇÃO DE PETS =====

def editar_pets(request, id):
    pets = get_object_or_404(Pet, pk=id)

    if request.method == 'POST':
        form = PetsForm(request.POST, instance=pets)

        if form.is_valid():
            form.save()
            return redirect('listar_pets')

    else:
        form = PetsForm(instance=pets)

    return render(request, 'pet/<editar_pets.html>', {'form': form, 'pets': pets})

# ===== EXCLUSÃO DE PETS =====

def excluir_pets(request, id):
    pets = get_object_or_404(Pet, pk=id)

    if request.method == 'POST':
        pets.delete()
        return redirect('listar_pets')

    return render(request, 'pet/<excluir_pets.html>', {'pets': pets})

# ===== HISTORICO DE LOCALIZAÇÃO =====

def historico_localizacao(request, id_coleira):
    # 1. Busca o Pet pela PK (id_coleira)
    pet = get_object_or_404(Pet, id_coleira=id_coleira)

    # 2. Validação de acesso do Tutor (ajuste conforme o sistema de login/sessão de vocês)
    # Exemplo assumindo que o id_usuario está na sessão:
    id_usuario = request.session.get('id_usuario')
    if not id_usuario:
        return redirect('login')  # Ajuste para o nome da rota de login de vocês

    vinculo = PetTutor.objects.filter(
        id_coleira=pet,
        id_tutor_id=id_usuario
    ).select_related('id_tutor').first()

    if not vinculo:
        messages.error(request, "Você não tem permissão para visualizar este pet.")
        return redirect('listar_pets')  # Ajuste para a rota principal de pets

    # 3. Tratamento da data selecionada (?data=YYYY-MM-DD)
    data_str = request.GET.get('data')
    if data_str:
        try:
            data_selecionada = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            data_selecionada = date.today()
    else:
        data_selecionada = date.today()

    data_anterior = data_selecionada - timedelta(days=1)
    data_proxima = data_selecionada + timedelta(days=1)

    # 4. Chama a regra de negócio no services.py
    dados_historico = obter_historico_diario(
        pet=pet,
        data_consulta=data_selecionada,
        tutor=vinculo.id_tutor
    )

    # 5. Contexto entregue para o template do Front-end
    context = {
        "pet": pet,
        "data_selecionada": data_selecionada,
        "data_anterior": data_anterior.strftime("%Y-%m-%d"),
        "data_proxima": data_proxima.strftime("%Y-%m-%d"),
        "bloquear_proxima": data_selecionada >= date.today(),  # Impede avançar para o futuro
        "registros": dados_historico["registros"],
        "total_registros": dados_historico["total_registros"],
        "total_saidas_raio": dados_historico["total_saidas_raio"],
        "centro_mapa": dados_historico["centro_mapa"],
    }

    # O pessoal do front-end vai criar/editar este arquivo HTML:
    return render(request, "pet/", context) # --> COLOCAR ROTA HTML DA TELA DO HISTORICO DE LOCALIZAÇAO