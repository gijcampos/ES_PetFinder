from math import radians, sin, cos, sqrt, atan2
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Notificacao
from pet.models import HistoricoLocalizacao

def calcular_distancia_metros(lat1, lon1, lat2, lon2):
    """Calcula a distância em metros entre duas coordenadas geográficas."""
    R = 6371000  # Raio da Terra em metros
    
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    
    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def processar_monitoramento_pet(pet, tutor, endereco_tutor_lat, endereco_tutor_lon):
    """
    Função principal que gerencia todas as regras da Issue #7:
    - Saída de raio (> 10m)
    - Retorno ao raio (<= 10m)
    - Perda de sinal GPS (sem atualização recente)
    """
    agora = timezone.now()
    
    # Acessa os dados do usuário a partir da relação OneToOne no model Tutor
    usuario = tutor.id_tutor 
    
    # Pega o histórico mais recente do pet
    historico_recente = HistoricoLocalizacao.objects.filter(id_coleira=pet).order_by('-data_hora').first()
    
    if not historico_recente:
        return  # Sem nenhuma localização registrada

    # --- 1. VERIFICAÇÃO DE PERDA DE SINAL GPS ---
    limiar_perda_sinal = agora - timedelta(hours=2)
    if historico_recente.data_hora < limiar_perda_sinal:
        ultima_alerta_gps = Notificacao.objects.filter(
            id_coleira=pet, 
            tipo=Notificacao.Tipo.AVISO_CONTATO
        ).order_by('-data_hora').first()
        
        if not ultima_alerta_gps or (agora - ultima_alerta_gps.data_hora) > timedelta(hours=24):
            mensagem_gps = (
                f"Olá {usuario.nome},\n\n"
                f"Aviso importante da equipe PetFinder:\n"
                f"Não recebemos atualizações de localização do pet {pet.nome} "
                f"desde {historico_recente.data_hora.strftime('%d/%m/%Y às %H:%M')}.\n"
                f"Pode haver perda de sinal GPS na coleira. Verifique o dispositivo!"
            )
            
            send_mail(
                subject='[Alerta] Possível perda de sinal GPS do pet',
                message=mensagem_gps,
                from_email='petfinder@gmail.com',
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            
            Notificacao.objects.create(
                id_usuario=usuario,
                id_tutor_origem=tutor,
                id_coleira=pet,
                tipo=Notificacao.Tipo.AVISO_CONTATO,
                data_hora=agora,
                mensagem=f"Perda de sinal GPS detectada para o pet {pet.nome}.",
                lida=False
            )
        return

    # --- 2. CÁLCULO DE DISTÂNCIA (SAÍDA E RETORNO AO RAIO) ---
    distancia = calcular_distancia_metros(
        lat1=endereco_tutor_lat, 
        lon1=endereco_tutor_lon, 
        lat2=float(historico_recente.latitude), 
        lon2=float(historico_recente.longitude)
    )
    
    ultima_movimentacao = Notificacao.objects.filter(
        id_coleira=pet, 
        tipo=Notificacao.Tipo.SAIDA_RAIO
    ).order_by('-data_hora').first()

    estava_fora = ultima_movimentacao and "saiu" in ultima_movimentacao.mensagem.lower()

    # CASO A: PET SAIU DO RAIO (> 10 metros)
    if distancia > 10:
        if not estava_fora or (agora - ultima_movimentacao.data_hora) > timedelta(minutes=5):
            
            mensagem_saida = (
                f"Olá {usuario.nome},\n\n"
                f"A equipe PetFinder gostaria de te notificar que o seu pet:\n"
                f"- Nome do pet: {pet.nome}\n"
                f"- ID do pet: {pet.id_coleira}\n"
                f"- Horário: {historico_recente.data_hora.strftime('%d/%m/%Y às %H:%M')}\n"
                f"- Localização atual: Lat {historico_recente.latitude}, Lon {historico_recente.longitude}\n\n"
                f"Saiu do seu endereço favoritado! Ele está a mais de 10m do raio da residência.\n"
                f"Fique atenta(o)!"
            )
            
            send_mail(
                subject='Seu pet saiu do endereço cadastrado!',
                message=mensagem_saida,
                from_email='petfinder@gmail.com',
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            
            Notificacao.objects.create(
                id_usuario=usuario, 
                id_tutor_origem=tutor,
                id_coleira=pet,
                tipo=Notificacao.Tipo.SAIDA_RAIO,
                data_hora=agora,
                mensagem=f"Pet {pet.nome} saiu do raio de 10m.",
                lida=False
            )

    # CASO B: PET RETORNOU PARA O RAIO SEGURO (<= 10 metros)
    elif distancia <= 10 and estava_fora:
        
        mensagem_retorno = (
            f"Olá {usuario.nome},\n\n"
            f"Boas notícias! O seu pet {pet.nome} retornou para dentro do raio de segurança de 10 metros "
            f"do endereço cadastrado às {historico_recente.data_hora.strftime('%H:%M')}.\n"
            f"Ele está seguro!"
        )
        
        send_mail(
            subject='Seu pet retornou para o raio seguro!',
            message=mensagem_retorno,
            from_email='petfinder@gmail.com',
            recipient_list=[usuario.email],
            fail_silently=False,
        )
        
        Notificacao.objects.create(
            id_usuario=usuario, 
            id_tutor_origem=tutor,
            id_coleira=pet,
            tipo=Notificacao.Tipo.SAIDA_RAIO,
            data_hora=agora,
            mensagem=f"Pet {pet.nome} retornou para dentro do raio de 10m.",
            lida=False
        )