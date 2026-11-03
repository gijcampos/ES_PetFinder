from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import Cadastro
from .forms import CadastroForm

# ===== Formulário de Cadastro =====

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)

        if form.is_valid():
            usuario = form.save(commit = False)
            # Transforma a senha em Hash
            usuario.senha = make_password(form.cleaned_data['senha'])
            usuario.save()

            #redirecionamento do Cadastro para o Login
            return redirect('login')
    else:
        form = CadastroForm()

    return render(request, 'usuarios/tela_cadastro.html', {'form': form})

# ===== Tela de Login =====

def login(request):
    return render(request, 'usuarios/login.html')

# ===== Edição Cadastro ==== 

def editar_perfil(request, id):
    cadastro = get_object_or_404(Cadastro, id=id)

    if request.method == 'POST':
        form = CadastroForm(request.POST, instance=cadastro)

        if form.is_valid():
            form.save()

            return redirect() # !!! COLOCAR UM REDIRECIONAMENTO PARA LISTA DE TUTORES !!!
    else:
        form = CadastroForm(instance=cadastro)

    return render(request, 'usuario/editar_perfil.html', {'form': form, 'cadastro': cadastro})

# ===== Excluir Cadastro =====

def excluir_perfil(request, id):
    cadastro = get_object_or_404(Cadastro, id=id)

    if request.method == 'POST':
        cadastro.delete()

        return redirect('cadastro')

    return render(request, 'usuario/excluir_perfil.html', {'cadastro': cadastro})