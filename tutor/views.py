from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import Usuario, Tutor
from pet.models import PetTutor
from pet.services import obter_status_tempo_real_pet
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
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')
        usuario = Usuario.objects.filter(email=email).first()

        if usuario and check_password(senha, usuario.senha_hash):
            request.session['id_usuario'] = usuario.id_usuario
            return redirect('core:index')
        else:
            messages.error(request, 'E-mail ou senha inválidos.')

    return render(request, 'tutor/login.html')

    return render(request, 'tutor/tela_login.html')
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

# ===== ALTERNAR MODO FORA DA CIDADE =====

def alternar_modo_fora_cidade(request, id_tutor):
    tutor = get_object_or_404(Tutor, pk=id_tutor)

    if not tutor.modo_fora_cidade:
        tem_contato = ContatoEmergencia.objects.filter(id_tutor=tutor).exists()
    if not tem_contato:
        messages.warning(
            request,
            "Você precisa cadastrar pelo menos um contato de emergência antes de ativar o modo 'Fora da cidade'."
        )
        return redirect('cadastro_emergencia', id_tutor=tutor.pk)
    
    tutor.modo_fora_cidade = not tutor.modo_fora_cidade
    tutor.save()

    status = "ativado" if tutor.modo_fora_cidade else "desativado"
    messages.success(request, f"Modo 'Fora da cidade' {status} com sucesso!")
    
    return redirect('listar_pets')  # --> Colocar uma Rota HTML que faça mais sentido.

# ===== AMBIENTE PRINCIPAL DO SITE =====

def ambiente_tutor(request):
    id_usuario = request.session.get('id_usuario')
    if not id_usuario:
        return redirect('tutor:login')

    usuario = get_object_or_404(Usuario, pk=id_usuario)
    tutor = Tutor.objects.filter(pk=id_usuario).first()

    pets = []
    pet_inicial = None
    if tutor:
        vinculos = PetTutor.objects.filter(id_tutor=tutor).select_related('id_coleira')
        pets = [v.id_coleira for v in vinculos]
        pet_inicial = obter_status_tempo_real_pet(pets[0], tutor=tutor) if pets else None

    return render(request, 'usuarios/ambiente_tutor.html', {
        'usuario': usuario,
        'tutor': tutor,
        'nome_tutor': usuario.nome,
        'pets': pets,
        'pet_inicial': pet_inicial,
    })

# ===== CAMPO DE LOGOUT =====

def sair(request):
    request.session.flush()
    return redirect('tutor:login')
