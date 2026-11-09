from django.shortcuts import render, redirect, get_object_or_404
from .models import Clinica
from .forms import ClinicaForm
from tutor.models import Cadastro

# ===== CADASTRO DA CLINICA =====

def cadastro(request, id_tutor):
    tutor = get_object_or_404(Cadastro, id=id_tutor)
    
    if request.method == 'POST':
        form = ClinicaForm(request.POST)
        
        if form.is_valid():
            clinica = form.save(commit=False)
            clinica.tutor = tutor
            
            # Tratamento de clínica preferida única
            if clinica.preferida:
                Clinica.objects.filter(tutor=tutor, preferida=True).update(preferida=False)
                
            clinica.save()
            return redirect('listar', id_tutor=tutor.id) # --> COLOCAR UMA ROTA HTML PARA REDIRECIONAR APOS SALVAR O CADASTRO !!!
    else:
        form = ClinicaForm()
        
    return render(request, 'clinica/', {'form': form, 'tutor': tutor}) # --> COLOCAR UMA ROTA HTML PARA O CADASTRO DE CLINICAS !!!

# ===== LISTAGEM DAS CLINICAS =====

def listar(request, id_tutor):
    tutor = get_object_or_404(Cadastro, id=id_tutor)
    
    clinicas = Clinica.objects.filter(tutor=tutor)
    
    return render(request, 'clinica/', {'clinicas': clinicas, 'tutor': tutor}) # --> COLOCAR UMA ROTA HMTL PARA A LISTAGEM DAS CLINICAS !!!

# ===== EDITAR =====

def editar(request, id_clinica):
    clinica = get_object_or_404(Clinica, id=id_clinica)
    
    if request.method == 'POST':
        form = ClinicaForm(request.POST, instance=clinica)
        
        if form.is_valid():
            
            if form.cleaned_data['preferida']:
                
                Clinica.objects.filter(tutor=clinica.tutor, preferida=True).update(preferida=False)
            form.save()
            
            return redirect('listar', id_tutor=clinica.tutor.id) # --> COLOCAR UMA ROTA HTML PARA REDIRECIONAR DEPOIS DE SALVAR AS ALTERAÇÕES !!!
    else:
        form = ClinicaForm(instance=clinica)
        
    return render(request, 'clinica/', {'form': form, 'clinica': clinica}) # --> COLOCAR UMA ROTA HTML PARA EDITAR O CADASTRO DA CLINICA !!!

# ===== EXCLUSÃO =====

def excluir(request, id_clinica):
    clinica = get_object_or_404(Clinica, id=id_clinica)
    
    tutor_id = clinica.tutor.id
    clinica.delete()

    return redirect('listar', id_tutor=tutor_id) # --> COLOCAR UMA ROTA HTML PARA DEPOIS DE EXCLUIR O CADASTRO DA CLINICA !!!