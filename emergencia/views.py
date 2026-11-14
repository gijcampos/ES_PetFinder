from django.shortcuts import render, redirect, get_object_or_404
from tutor.models import Tutor
from .forms import ContatoEmergenciaForm
from .models import ContatoEmergencia


def cadastro(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)

    if request.method == 'POST':
        form = ContatoEmergenciaForm(request.POST)

        if form.is_valid():
            form.save_para_tutor(tutor)
            return redirect('listar_emergencia', id_tutor=id_tutor)
    else:
        form = ContatoEmergenciaForm()

    return render(request, 'emergencia/cadastro.html', {'form': form, 'tutor': tutor})  # --> CRIAR ESSE HTML


def editar(request, id_tutor, id_contato):
    contato = get_object_or_404(ContatoEmergencia, id_tutor=id_tutor, id_contato=id_contato)

    if request.method == 'POST':
        form = ContatoEmergenciaForm(request.POST, instance=contato)

        if form.is_valid():
            form.save_para_tutor(contato.id_tutor)
            return redirect('listar_emergencia', id_tutor=id_tutor)
    else:
        form = ContatoEmergenciaForm(instance=contato)

    return render(request, 'emergencia/editar.html', {'form': form, 'contato': contato})  # --> CRIAR ESSE HTML


def excluir(request, id_tutor, id_contato):
    contato = get_object_or_404(ContatoEmergencia, id_tutor=id_tutor, id_contato=id_contato)

    if request.method == 'POST':
        contato.delete()
        return redirect('listar_emergencia', id_tutor=id_tutor)

    return render(request, 'emergencia/excluir.html', {'contato': contato})  # --> CRIAR ESSE HTML


def listar(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)
    contatos = ContatoEmergencia.objects.filter(id_tutor=tutor).select_related('id_contato')

    return render(request, 'emergencia/listar.html', {'contatos': contatos, 'tutor': tutor})  # --> CRIAR ESSE HTML