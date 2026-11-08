from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContatoEmergenciaForm
from tutor.models import Cadastro

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