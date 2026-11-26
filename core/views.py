from django.shortcuts import render, redirect, get_object_or_404
from tutor.models import Usuario

def index(request):
    id_usuario = request.session.get("id_usuario")
    if not id_usuario:
        return redirect("tutor:login")

    usuario = get_object_or_404(Usuario, pk=id_usuario)
    return render(request, "core/index.html", {"usuario": usuario})