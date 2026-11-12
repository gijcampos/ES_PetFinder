from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from .models import Usuario
from .forms import CadastroForm

# ===== Arquivo que lida com as criações e validações dos formularios =====

def cadastro(request):
    # Verifique se o usuario apertou Enter
    if request.method == 'POST': 
        form = CadastroForm(request.POST)
        # Executa automaticamente as validações pelo próprio Django
        if form.is_valid():
            usuario = form.save(commit = False)
            #Pega a senha e a transforma em hash
            usuario.senha_hash = make_password(form.cleaned_data['senha'])
            usuario.save()

            #Redireciona o Cadastro para o Login
            return redirect('login') 

    else:
        form = CadastroForm()

    return render(request, 'usuarios/<tela_do_cadastro.html>', {'form': form}) # !!! MUDAR <tela_do_cadastro.html> PARA SEU RESPECTIVO ARQUIVO QUANDO HOUVER A TELA DE CADASTRO !!!

# ===== Tela de Login =====

def login_view(request):
    return render(request, 'usuarios/usuario_login.html')

# ===== Funções de Edição e Exclusão do formulário de Cadastro =====

def editar_perfil(request, id): #Solicita o ID do cadastro do usuario
    cadastro = get_object_or_404(Usuario, pk=id) #Faz a busca se não retornar nada aparece o erro 404;

    if request.method == 'POST':
        
        form = CadastroForm(request.POST, instance=cadastro)
        
        if form.is_valid():
            form.save()
            return redirect('perfil_sucesso', id=cadastro.id)
    
    else:
        form = CadastroForm(instance=cadastro)

    return render(
        request, 'usuarios/<editar_perfil.html>', {'form': form, 'cadastro': cadastro}
    )

def excluir_perfil(request, id):
    cadastro = get_object_or_404(Usuario, pk=id)

    if request.method == 'POST':
        cadastro.delete()
        
        return redirect(
            'cadastro'
        )

    return render(
        request, 'usuarios/<excluir_perfil.html>', {'cadastro': cadastro}
    )