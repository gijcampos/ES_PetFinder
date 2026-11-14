from datetime import datetime, time, timedelta
import holidays
from django.utils import timezone
from .models import Clinica, TutorClinica

FERIADOS_BR = holidays.Brazil(state='PR')

NOMES_DIAS = {
    1: "Domingo",
    2: "Segunda-feira",
    3: "Terça-feira",
    4: "Quarta-feira",
    5: "Quinta-feira",
    6: "Sexta-feira",
    7: "Sábado",
}


def eh_feriado(data_obj) -> bool:
    """Verifica se uma data é feriado nacional ou estadual (PR)."""
    return data_obj in FERIADOS_BR


def _horario_eh_24h(horario) -> bool:
    """Considera 24h se abre 00:00 e fecha 23:59 (ou se abre == fecha)."""
    if not horario:
        return False
    if horario.abre == horario.fecha:
        return True
    if horario.abre == time(0, 0) and horario.fecha >= time(23, 59):
        return True
    return False


def _buscar_proxima_abertura(horarios_por_dia: dict, agora: datetime) -> str:
    """
    Calcula texto amigável para o próximo horário de abertura quando fechada.
    Ex: 'Abre hoje às 08:00', 'Abre amanhã às 08:00' ou 'Abre Segunda-feira às 08:00'.
    """
    dia_atual_iso = agora.isoweekday()  # 1 = Segunda ... 7 = Domingo
    hora_atual = agora.time()

    # 1. Verifica se ainda vai abrir hoje (e hoje não é feriado)
    if not eh_feriado(agora.date()) and dia_atual_iso in horarios_por_dia:
        h_hoje = horarios_por_dia[dia_atual_iso]
        if hora_atual < h_hoje.abre:
            return f"Abre hoje às {h_hoje.abre.strftime('%H:%M')}"

    # 2. Varre os próximos 7 dias pulando feriados (a menos que seja 24h)
    for offset in range(1, 8):
        data_futura = agora.date() + timedelta(days=offset)
        dia_futuro_iso = data_futura.isoweekday()

        if dia_futuro_iso in horarios_por_dia:
            h_futuro = horarios_por_dia[dia_futuro_iso]
            if eh_feriado(data_futura) and not _horario_eh_24h(h_futuro):
                continue

            hora_fmt = "00:00 (24h)" if _horario_eh_24h(h_futuro) else h_futuro.abre.strftime("%H:%M")
            if offset == 1:
                return f"Abre amanhã às {hora_fmt}"
            return f"Abre {NOMES_DIAS[dia_futuro_iso]} às {hora_fmt}"

    return "Horário indisponível"


def verificar_status_clinica(clinica: Clinica, agora: datetime = None) -> dict:
    """
    Avalia se uma clínica está 'ABERTA' ou 'FECHADA' no fuso horário local,
    considerando suporte a 24h, feriados e próximo horário de abertura.
    """
    if agora is None:
        agora = timezone.localtime(timezone.now())

    dia_semana_iso = agora.isoweekday()  # 1 (Seg) a 7 (Dom)
    hora_atual = agora.time()
    horarios_por_dia = {h.dia_semana: h for h in clinica.horarios.all()}

    horario_hoje = horarios_por_dia.get(dia_semana_iso)
    eh_24h = _horario_eh_24h(horario_hoje)
    hoje_feriado = eh_feriado(agora.date())

    aberta = False
    detalhe_horario = ""

    if horario_hoje:
        if eh_24h:
            aberta = True
            detalhe_horario = "Atendimento 24 horas"
        elif not hoje_feriado:
            if horario_hoje.abre <= horario_hoje.fecha:
                aberta = horario_hoje.abre <= hora_atual <= horario_hoje.fecha
            else:
                aberta = hora_atual >= horario_hoje.abre or hora_atual <= horario_hoje.fecha

            if aberta:
                detalhe_horario = f"Fecha às {horario_hoje.fecha.strftime('%H:%M')}"

    if not aberta:
        proxima = _buscar_proxima_abertura(horarios_por_dia, agora)
        detalhe_horario = f"Feriado • {proxima}" if hoje_feriado else proxima

    return {
        "aberta": aberta,
        "status_texto": "ABERTA" if aberta else "FECHADA",
        "detalhe_horario": detalhe_horario,
        "eh_24h": eh_24h,
    }


def listar_clinicas_com_status(tutor=None, termo_busca: str = "") -> list:
    """
    Lista clínicas filtradas por nome (opcional), ordenando favoritas primeiro
    e anexando o status de funcionamento em tempo real.
    """
    queryset = Clinica.objects.prefetch_related('horarios').all()

    if termo_busca:
        queryset = queryset.filter(nome__icontains=termo_busca.strip())

    favoritas_ids = set()
    if tutor:
        favoritas_ids = set(
            TutorClinica.objects.filter(id_tutor=tutor).values_list('id_clinica_id', flat=True)
        )

    agora = timezone.localtime(timezone.now())
    resultado = []

    for clinica in queryset:
        status_info = verificar_status_clinica(clinica, agora=agora)
        resultado.append({
            "id_clinica": clinica.id_clinica,
            "nome": clinica.nome,
            "endereco": clinica.endereco,
            "telefone": clinica.telefone,
            "favorita": clinica.id_clinica in favoritas_ids,
            **status_info,
        })

    resultado.sort(key=lambda c: (not c["favorita"], c["nome"].lower()))
    return resultado