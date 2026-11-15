from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Agendamento
from tutor.models import Tutor
from pet.models import Pet
from clinica.models import Clinica

def criar_agendamento(request):
    # Se o usuário acessou a página apenas para visualizar o formulário (GET)
    if request.method == 'GET':
        # Você pode mandar dados do banco para preencher as opções (os <select>) no HTML
        contexto = {
            'clinicas': Clinica.objects.all(),
            'pets': Pet.objects.all(), # Idealmente, filtrar apenas os pets do tutor logado
        }
        return render(request, 'agendamentos/novo_agendamento.html', contexto) # --> COLOCAR ROTA HTML PARA CRIAR NOVO AGENDAMENTO

    # Se o usuário clicou no botão "Confirmar agendamento" do formulário (POST)
    elif request.method == 'POST':
        try:
            # Em templates HTML, pegamos os dados do 'name' dos inputs usando request.POST
            tutor_id = request.POST.get('id_tutor') 
            coleira_id = request.POST.get('id_coleira')
            clinica_id = request.POST.get('id_clinica')
            tipo_atendimento = request.POST.get('tipo_atendimento', 'consulta')
            data_hora_str = request.POST.get('data_hora')
            
            # O input type="datetime-local" do HTML costuma enviar no formato com "T"
            data_hora = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')
            
            hora = data_hora.hour
            dia_semana = data_hora.weekday() 
            
            # REGRAS DE FUNCIONAMENTO
            if dia_semana == 6:
                messages.error(request, 'A clínica não abre aos domingos.')
                return redirect('criar_agendamento') # --> ROTA DE CRIAÇÃO DO AGENDAMENTO
                
            if dia_semana == 5 and hora >= 12:
                messages.error(request, 'Aos sábados, a clínica atende apenas até as 12:00.')
                return redirect('criar_agendamento') # --> ROTA DE CRIAÇÃO DO AGENDAMENTO
                
            if hora < 8 or hora >= 18:
                messages.error(request, 'Horário fora do funcionamento (08:00 às 18:00).')
                return redirect('criar_agendamento') # --> ROTA DE CRIAÇÃO DO AGENDAMENTO

            # REGRA DE DISPONIBILIDADE
            if Agendamento.objects.filter(id_clinica_id=clinica_id, data_hora=data_hora).exists():
                messages.warning(request, 'Este horário já está reservado. Selecione outro na grade.')
                return redirect('criar_agendamento') # --> ROTA DE CRIAÇÃO DO AGENDAMENTO

            # BUSCA INSTÂNCIAS E SALVA
            tutor_obj = get_object_or_404(Tutor, pk=tutor_id)
            pet_obj = get_object_or_404(Pet, pk=coleira_id)
            clinica_obj = get_object_or_404(Clinica, pk=clinica_id)

            Agendamento.objects.create(
                id_tutor=tutor_obj,
                id_coleira=pet_obj,
                id_clinica=clinica_obj,
                data_hora=data_hora,
                tipo_atendimento=tipo_atendimento
            )
            
            # Mensagem de sucesso e redirecionamento para alguma pagina após o sucesso
            messages.success(request, 'Agendamento confirmado com sucesso!')

            return redirect('home') # --> COLOCAR ROTA HTML PARA MENSAGEM DE SUCESSO OU QUALLQUER OUTRA ROTA

        except Exception as e:
            messages.error(request, f'Erro ao processar: {str(e)}')
            return redirect('criar_agendamento') # --> COLOCAR UMA ROTA HTML PARA REDIRECIONAMENTO CASO DE ERRADO


def cancelar_agendamento(request, id_agendamento):

    if request.method == 'POST':
        agendamento = get_object_or_404(Agendamento, id_agendamento=id_agendamento)
        agendamento.delete()
        
        messages.success(request, 'Agendamento cancelado com sucesso.')

        return redirect('meus_agendamentos') # --> COLOCAR ROTA HTML PARA LISTAGEM DE AGENDAMENTOS