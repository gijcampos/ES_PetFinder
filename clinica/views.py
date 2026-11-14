from django.shortcuts import render, redirect, get_object_or_404
from .models import Clinica, TutorClinica
from .forms import ClinicaForm
from tutor.models import Tutor
from .services import listar_clinicas_com_status

# ===== CADASTRO DA CLINICA =====

def cadastro(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)
    
    if request.method == 'POST':
        form = ClinicaForm(request.POST)
        
        if form.is_valid():
            clinica = form.save()
            
            # Se a lógica do seu formulário permitir favoritar na hora do cadastro:
            # (Verifique se o seu form tem o campo preferida/favorita)
            if form.cleaned_data.get('preferida'):
                TutorClinica.objects.get_or_create(id_tutor=tutor, id_clinica=clinica)
            
            return redirect('listar_clinicas', id_tutor=tutor.pk) 
    else:
        form = ClinicaForm()
        
    return render(request, 'clinica/', {'form': form, 'tutor': tutor}) # --> COLOCAR UMA ROTA HTML PARA TELA DE CADASTRO

# ===== LISTAGEM DAS CLINICAS =====

def listar(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)
    termo_busca = request.GET.get('q', '')
    apenas_abertas = request.GET.get('apenas_abertas') in ['1', 'true', 'on']

    clinicas = listar_clinicas_com_status(
        tutor=tutor,
        termo_busca=termo_busca,
        apenas_abertas=apenas_abertas
    )

    context = {
        'clinicas': clinicas,
        'tutor': tutor,
        'termo_busca': termo_busca,
        'apenas_abertas': apenas_abertas,
    }

    return render(request, 'clinica/', context)  # --> COLOCAR UMA ROTA HTML PARA A LISTAGEM DAS CLINICAS

# ===== CLINICA FAVORITA =====

def favorita(request, id_tutor, id_clinica):
    """Favorita ou desfavorita uma clínica (estrela) para o tutor."""
    if request.method == 'POST':
        tutor = get_object_or_404(Tutor, pk=id_tutor)
        clinica = get_object_or_404(Clinica, pk=id_clinica)

        vinculo = TutorClinica.objects.filter(id_tutor=tutor, id_clinica=clinica)
        if vinculo.exists():
            vinculo.delete()
        else:
            TutorClinica.objects.create(id_tutor=tutor, id_clinica=clinica)

    return redirect('listar_clinicas', id_tutor=id_tutor)

# ===== EDITAR =====

def editar(request, id_clinica):
    clinica = get_object_or_404(Clinica, pk=id_clinica)
    
    if request.method == 'POST':
        form = ClinicaForm(request.POST, instance=clinica)
        
        if form.is_valid():
            form.save()
            return redirect('listar_clinicas') # Ajuste a rota de redirecionamento conforme seu urls.py
    else:
        form = ClinicaForm(instance=clinica)
        
    return render(request, 'clinica/', {'form': form, 'clinica': clinica}) # --> COLOCAR UMA ROTA HTML PARA A EDIÇÃO DA CLINICA

# ===== EXCLUSÃO =====

def excluir(request, id_clinica):
    clinica = get_object_or_404(Clinica, pk=id_clinica)
    clinica.delete()

    return redirect('listar_clinicas') # --> COLOCAR UMA ROTA HTML PARA O REDIRECIONAR DEPOIS DE APAGAR A CLINICA