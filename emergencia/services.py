# emergencia/services.py
from django.core.mail import send_mail
from django.conf import settings
from emergencia.models import ContatoEmergencia

def notificar_contatos_emergencia(pet, tutor, ultima_localizacao, distancia_metros):
    if not tutor.modo_fora_cidade:
        return False

    contatos = ContatoEmergencia.objects.filter(id_tutor=tutor)
    if not contatos.exists():
        return False

    # Monta link do Google Maps com a última coordenada
    link_mapa = f"https://www.google.com/maps?q={ultima_localizacao.latitude},{ultima_localizacao.longitude}"
    telefone_tutor = getattr(tutor, 'telefone', 'Não informado')

    for contato in contatos:
        if not contato.email:
            continue

        assunto = "Contato de emergência - o pet saiu do endereço cadastrado!"
        mensagem = (
            f"Olá {contato.nome},\n\n"
            f"A equipe PetFinder gostaria de te notificar que o pet que você é contato de emergência:\n\n"
            f"Nome do pet: {pet.nome}\n"
            f"ID do pet: {pet.id_coleira}\n"
            f"Última localização: {link_mapa}\n"
            f"Contato do tutor ({tutor.id_usuario.nome}): {telefone_tutor} | {tutor.id_usuario.email}\n\n"
            f"Saiu do endereço favoritado, ele está a mais de {int(distancia_metros)}m do raio da residência!\n"
            f"Fique atento(a), e qualquer coisa retorne à casa para encontrá-lo!"
        )

        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contato.email],
            fail_silently=False,
        )
    return True