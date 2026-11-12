import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

# Importe os models diretamente dos seus apps
from .models import Agendamento
from tutor.models import Tutor
from pet.models import Pet
from clinica.models import Clinica

@csrf_exempt
def criar_agendamento(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            tutor_id = dados.get('id_tutor')
            coleira_id = dados.get('id_coleira')
            clinica_id = dados.get('id_clinica')
            tipo_atendimento = dados.get('tipo_atendimento', 'consulta')
            
            data_hora_str = dados.get('data_hora')
            data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
            
            # =========================================================
            # REGRA 1: Bloqueio de horários fora do funcionamento
            # =========================================================
            hora_agendamento = data_hora.hour
            dia_semana = data_hora.weekday() 
            
            if dia_semana == 6:
                return JsonResponse({'erro': 'A clínica não abre aos domingos.'}, status=400)
            if dia_semana == 5 and hora_agendamento >= 12:
                return JsonResponse({'erro': 'Aos sábados, a clínica atende apenas até as 12:00.'}, status=400)
            if hora_agendamento < 8 or hora_agendamento >= 18:
                return JsonResponse({'erro': 'Horário fora do funcionamento (08:00 às 18:00).'}, status=400)

            # =========================================================
            # REGRA 2: Aviso de indisponibilidade
            # =========================================================
            # Como filtramos por ID na tabela, podemos usar "_id" para buscar direto na coluna da FK
            horario_ocupado = Agendamento.objects.filter(id_clinica_id=clinica_id, data_hora=data_hora).exists()
            
            if horario_ocupado:
                return JsonResponse({
                    'erro': 'Este horário já está reservado.',
                    'sugestoes': 'Por favor, selecione outro horário na grade.'
                }, status=409)

            # =========================================================
            # NOVO PASSO: Buscar as instâncias reais no banco
            # =========================================================
            # Isso garante que o Tutor, o Pet e a Clínica realmente existem antes de agendar
            tutor_obj = get_object_or_404(Tutor, pk=tutor_id)
            pet_obj = get_object_or_404(Pet, pk=coleira_id)
            clinica_obj = get_object_or_404(Clinica, pk=clinica_id)

            # =========================================================
            # REGRA 3: Salvar no banco passando as instâncias
            # =========================================================
            novo_agendamento = Agendamento.objects.create(
                id_tutor=tutor_obj,     # Passamos o objeto inteiro, não apenas o ID numérico
                id_coleira=pet_obj,     # Passamos o objeto inteiro
                id_clinica=clinica_obj, # Passamos o objeto inteiro
                data_hora=data_hora,
                tipo_atendimento=tipo_atendimento
            )
            
            return JsonResponse({
                'mensagem': 'Agendamento confirmado com sucesso!',
                'id_agendamento': novo_agendamento.id_agendamento
            }, status=201)

        except Exception as e:
            return JsonResponse({'erro': f'Erro ao processar os dados: {str(e)}'}, status=400)
            
    return JsonResponse({'erro': 'Método não permitido. Use POST.'}, status=405)

# ===== CANCELAMENTO =====

@csrf_exempt
def cancelar_agendamento(request, id_agendamento):
    if request.method == 'DELETE':
        agendamento = get_object_or_404(Agendamento, id_agendamento=id_agendamento)
        agendamento.delete()
        
        return JsonResponse({'mensagem': 'Agendamento cancelado e horário liberado.'}, status=200)
        
    return JsonResponse({'erro': 'Método não permitido. Use DELETE.'}, status=405)