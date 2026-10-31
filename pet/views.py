from django.shortcuts import render, redirect, get_object_or_404
from .models import Pet
from .forms import PetForm

# ===== LISTAR PETS =====

def listar_pets(request):
    pet = Pet.objects.all()

        # !!! FALTA COLOCAR O CAMINHO DO HTML DE LISTAGEM DE PETS !!!
    return render(request, 'pet/', {'pet': pet})

# ===== CADASTRAR PETS =====

def cadastrar(request):
    if request.method == 'POST':
        form = PetForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("listar_pets")

    else:
        form = PetForm()

    # !!! FALTA COLOCAR O CAMINHO DO HTML DE CADASTRO DE PET !!!
    return render(request, 'pet/', {'form': form})

# ===== EDIÇÃO DE PETS =====

def editar(request, id):
    pet = get_object_or_404(Pet, id=id)

    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)

        if form.is_valid():
            form.save()
            return redirect('listar_pets')

    else:
        form = PetForm(instance=pet)

    # !!! FALTA COLOCAR O CAMINHO DO HTML DE EDIÇÃO DE PET !!!
    return render(request, 'pet/', {'form': form, 'pet': pet})

# ===== EXCLUSÃO DE PETS =====

def excluir(request, id):
    pet = get_object_or_404(Pet, id=id)

    if request.method == 'POST':
        pet.delete()
        return redirect('listar_pets')

    # !!! FALTA COLOCAR O CAMINHO DO HTML DE EXCLUSÃO DE PET !!!
    return render(request, 'pet/', {'pet': pet})