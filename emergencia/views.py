from django.shortcuts import render, redirect, get_object_or_404
from .models import ContatoEmergencia
from .forms import ContatoEmergenciaForm
from tutor.models import Tutor

# ===== CADASTRO =====

def cadastro(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)
    
    if request.method == 'POST':
        form = ContatoEmergenciaForm(request.POST)
        
        if form.is_valid():
            contato = form.save(commit=False)
            contato.id_tutor = tutor  # Atribui o tutor correto ao campo do model
            contato.save()
            
            return redirect('listar_emergencia', id_tutor=tutor.pk)  # Ajuste para a rota de listagem
    else:
        form = ContatoEmergenciaForm()
        
    return render(request, 'emergencia/', {'form': form, 'tutor': tutor}) # --> COLOCAR ROTA HTML PARA CADASTRO DE CONTATO DE EMERGENCIA

# ===== LISTAGEM =====

def listar(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)
    
    # Filtra usando o nome correto do campo no model: id_tutor
    contatos = ContatoEmergencia.objects.filter(id_tutor=tutor)
    
    return render(request, 'emergencia/', {'contatos': contatos, 'tutor': tutor}) # --> COLOCAR ROTA HTML DE LISTAGEM DOS CONTATOS

# ===== EDIÇÃO =====
# Nota: Como a tabela usa chave primária composta (id_contato, id_tutor), 
# o ideal é receber ambos na URL para buscar o registro exato.

def editar(request, id_contato, id_tutor):
    contato = get_object_or_404(ContatoEmergencia, id_contato=id_contato, id_tutor=id_tutor)
    
    if request.method == 'POST':
        form = ContatoEmergenciaForm(request.POST, instance=contato)
        
        if form.is_valid():
            form.save()
            return redirect('listar_emergencia', id_tutor=contato.id_tutor.pk)
    else:
        form = ContatoEmergenciaForm(instance=contato)
        
    return render(request, 'emergencia/', {'form': form, 'contato': contato}) # --> COLOCAR ROTA HTML PARA EDIÇÃO DE CONTATO

# ===== EXCLUSÃO =====

def excluir(request, id_contato, id_tutor):
    contato = get_object_or_404(ContatoEmergencia, id_contato=id_contato, id_tutor=id_tutor)
    tutor_id = contato.id_tutor.pk
    contato.delete()

    return redirect('listar_emergencia', id_tutor=tutor_id) # --> COLOCAR UMA ROTA PARA REDIRECIONAR DEPOIS DE APAGAR UM CONTATO