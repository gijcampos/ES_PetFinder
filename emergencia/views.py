from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContatoEmergenciaForm
from tutor.models import Cadastro
from .models import ContatoEmergencia

def cadastro(request, id_tutor):
    tutor = get_object_or_404(Cadastro, id=id_tutor)

    if request.method == 'POST':
        form = ContatoEmergenciaForm(request.POST)

        if form.is_valid():
            contato = form.save(commit=False)
            contato.tutor = tutor
            contato.save()

            return redirect() # --> ALGUMA ROTA HTML PARA DEPOIS DE SALVAR O CONTATO !!!

    else:
        form = ContatoEmergenciaForm()

    return render(request, 'emergencia/', {'form': form, 'tutor': tutor}) # --> ALGUMA ROTA HMTL PARA A TELA DE CADASTRO !!!

# ===== EDIÇÃO =====    

def editar(request, id_contato):
    contato = get_object_or_404(ContatoEmergencia, id=id_contato)

    if request.method == 'POST':
        form = ContatoEmergenciaForm(request.POST, instance=contato)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = ContatoEmergenciaForm(instance=contato)

    return render(request, 'emergencia/', {'form': form, 'contato': contato}) # --> COLOCAR ALGUMA ROTA HTML PARA EDIÇÃO DE CADASTRO !!!

# ===== EXCLUSÃO =====

def excluir(request, id_contato):
    contato = get_object_or_404(ContatoEmergencia, id=id_contato)

    if request.method == 'POST':
        contato.delete()

        return redirect('login') # --> COLOCAR ALGUMA ROTA PARA DEPOIS DA EXCLUSÃO DO CONTATO DE EMERGENCIA !!!

    return render(request, 'emergencia/', {'contato': contato}) # --> COLOCAR ALGUMA ROTA PARA A TELA DE EXCLUSÃO DE CONTATO !!!

# ===== LISTAGEM =====

def listar(request, id_tutor):
    tutor = get_object_or_404(Cadastro, id=id_tutor)

    contatos = ContatoEmergencia.objects.filter(tutor=tutor)

    return render(request, 'emergencia/', {'contatos': contatos, 'tutor': tutor}) # --> COLOCAR UMA ROTA HTML PARA A LISTAGEM DE CONTATOS DE EMERGERNCIA !!!
