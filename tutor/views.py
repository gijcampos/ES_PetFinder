from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Tutor
from .forms import CadastroForm
from django.contrib import messages
from emergencia.models import ContatoEmergencia

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
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        usuario = Usuario.objects.filter(email=email).first()

        if usuario and check_password(senha, usuario.senha_hash):
            request.session['id_usuario'] = usuario.id_usuario
            return redirect('listar_pets')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'usuarios/usuario_login.html')

# ===== Funções de Edição e Exclusão do formulário de Cadastro =====

def editar_perfil(request, id): #Solicita o ID do cadastro do usuario
    cadastro = get_object_or_404(Usuario, pk=id) #Faz a busca se não retornar nada aparece o erro 404;

    if request.method == 'POST':
        
        form = CadastroForm(request.POST, instance=cadastro)
        
        if form.is_valid():
            form.save()
            return redirect('perfil_sucesso', id=cadastro.id_usuario)
    
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

# ===== MODO FORA DA CIDADE =====

def alternar_modo_fora_cidade(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)

    # Se o tutor está tentando ATIVAR o modo agora
    if not tutor.modo_fora_cidade:
        tem_contato = ContatoEmergencia.objects.filter(id_tutor=tutor).exists()
        if not tem_contato:
            messages.warning(
                request,
                "Você precisa cadastrar pelo menos um contato de emergência antes de ativar o modo 'Fora da cidade'."
            )
            return redirect('cadastro_emergencia', id_tutor=tutor.pk)

    # Alterna (ativa se estava False, desativa se estava True)
    tutor.modo_fora_cidade = not tutor.modo_fora_cidade
    tutor.save()

    status = "ativado" if tutor.modo_fora_cidade else "desativado"
    messages.success(request, f"Modo 'Fora da cidade' {status} com sucesso!")
    return redirect('listar_pets')  # --> Colocar uma Rota HTML que faça mais sentido.