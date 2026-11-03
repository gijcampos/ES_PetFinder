from django.shortcuts import render, redirect, get_object_or_404
from .models import Endereco
from .forms import EndForm

# ===== CADASTRAR ENDEREÇO =====

def cadastrar(request):
    if request.method == 'POST':
        form = EndForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect() # POSSIVEL TELA HTML DE REDIRECIONAMENTO PARA DEPOIS DE CADASRTRAR UM ENDEREÇO

    else:
        form = EndForm()

    # !!! COLOCAR CAMINHO HTML DA TELA DE CADASTRO DE ENDEREÇO !!!
    return render(request, 'endereco/', {'form': form})

# ===== EDITAR ENDEREÇO =====

def editar(request, id):
    endereco = get_object_or_404(Endereco, id=id)

    if request.method == 'POST':
        form = EndForm(request.POST, instance=endereco)

        if form.is_valid():
            form.save()
            return redirect('') # COLOCAR POSSIVEL TELA DE LISTAGEM OU EDIÇÃO
    else:
        form = EndForm(instance=endereco)

    # !!! COLOCAR CAMINHO DO HTML DE EDICAO DE ENDERECO !!!
    return render(request, 'endereco/', {'form': form, 'endereco': endereco})

# ===== EXCLUIR ENDEREÇO =====

def excluir(request, id):
    endereco = get_object_or_404(Endereco, id=id)
    
    if request.method == 'POST':
        endereco.delete()
        return redirect('') # POSSIVEL CAMINHO PARA REDIRECIONAR DEPOIS DE EXCLUIR ENDEREÇO

    # !!! COLOCAR CAMINHO DO HTML PARA REDIRECIONAR DEPOIS DA EXCLUSÃO DE ENDEREÇO JÁ CADASTRADO !!!
    return render(request, 'endereco/', {'endereco': endereco})