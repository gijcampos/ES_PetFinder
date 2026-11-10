from django.shortcuts import render, redirect, get_object_or_404
from .models import Clinica, TutorClinica
from .forms import ClinicaForm
from tutor.models import Tutor

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
    
    # Se quiser listar todas as clínicas cadastradas no sistema:
    # clinicas = Clinica.objects.all()
    
    # Ou se quiser listar apenas as clínicas favoritas/vinculadas a este tutor específico:
    ids_clinicas = TutorClinica.objects.filter(id_tutor=tutor).values_list('id_clinica', flat=True)
    clinicas = Clinica.objects.filter(pk__in=ids_clinicas)
    
    return render(request, 'clinica/', {'clinicas': clinicas, 'tutor': tutor}) # --> COLOCAR UMA ROTA HMTL PARA A LISTAGEM DAS CLINICAS

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