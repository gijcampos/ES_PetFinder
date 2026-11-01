from django.shortcuts import render, redirect, get_object_or_404
from .models import Pet
from .forms import PetsForm

def listar_pets(request):
    pets = Pet.objects.all()
    return render(request, 'pets/<listar_pets.html>', {'pets': pets})

def cadastrar_pets(request):
    if request.method == 'POST':
        form = PetsForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("listar_pets")

    else:
        form = PetsForm()
    return render(request, 'pets/cadastrar_pets.html', {'form': form})

# ===== EDIÇÃO DE PETS =====

def editar_pets(request, id):
    pets = get_object_or_404(Pet, pk=id)

    if request.method == 'POST':
        form = PetsForm(request.POST, instance=pets)

        if form.is_valid():
            form.save()
            return redirect('listar_pets')

    else:
        form = PetsForm(instance=pets)

    return render(request, 'pets/<editar_pets.html>', {'form': form, 'pets': pets})

# ===== EXCLUSÃO DE PETS =====

def excluir_pets(request, id):
    pets = get_object_or_404(Pet, pk=id)

    if request.method == 'POST':
        pets.delete()
        return redirect('listar_pets')

    return render(request, 'pets/<excluir_pets.html>', {'pets': pets})