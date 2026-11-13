import math
from datetime import date
from .models import HistoricoLocalizacao, PetTutor
from endereco.models import Endereco

RAIO_SEGURO_PADRAO_METROS = 100


def calcular_distancia_metros(lat1, lon1, lat2, lon2) -> int:
    """
    Calcula a distância em metros entre duas coordenadas (latitude/longitude)
    utilizando a Fórmula de Haversine.
    """
    raio_terra_metros = 6371000

    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(raio_terra_metros * c)


def obter_endereco_base_pet(pet, tutor=None):
    """
    Busca o endereço base (com latitude e longitude cadastradas) do tutor do pet.
    Se o tutor logado não for passado, busca pelo primeiro vínculo em PetTutor.
    """
    if tutor is None:
        vinculo = PetTutor.objects.filter(id_coleira=pet).select_related('id_tutor').first()
        if not vinculo:
            return None
        tutor = vinculo.id_tutor

    return Endereco.objects.filter(
        id_tutor=tutor,
        latitude__isnull=False,
        longitude__isnull=False
    ).first()


def obter_historico_diario(pet, data_consulta: date, tutor=None, raio_seguro_metros: int = RAIO_SEGURO_PADRAO_METROS):
    """
    Busca e processa os registros de localização de um pet em uma data específica,
    comparando com o endereço base do tutor para detectar saídas do raio.
    """
    endereco_base = obter_endereco_base_pet(pet, tutor=tutor)

    registros = HistoricoLocalizacao.objects.filter(
        id_coleira=pet,
        data_hora__date=data_consulta
    )

    linha_do_tempo = []
    total_saidas_raio = 0
    estava_fora = False

    # Texto amigável do endereço de casa (ex: "Rua Guarapuava, Nº 0000")
    texto_casa = "Endereço cadastrado"
    if endereco_base:
        num = endereco_base.numero if endereco_base.numero else "S/N"
        texto_casa = f"{endereco_base.logradouro}, Nº {num}"

    for reg in registros:
        fora_do_raio = False
        distancia = None

        if endereco_base:
            distancia = calcular_distancia_metros(
                endereco_base.latitude,
                endereco_base.longitude,
                reg.latitude,
                reg.longitude
            )
            fora_do_raio = distancia > raio_seguro_metros

        # Define título e subtítulo conforme o protótipo (HU008)
        if fora_do_raio:
            total_saidas_raio += 1
            titulo = "SAÍDA DO RAIO"
            subtitulo = f"Fora do raio seguro • {distancia} m de casa"
        elif estava_fora and not fora_do_raio:
            titulo = "Voltou ao raio seguro"
            subtitulo = f"Dentro do raio | {texto_casa}"
        else:
            titulo = "Em casa"
            subtitulo = f"Dentro do raio | {texto_casa}"

        estava_fora = fora_do_raio

        linha_do_tempo.append({
            "id": reg.id_localizacao,
            "horario": reg.data_hora.strftime("%H:%M"),
            "latitude": float(reg.latitude),
            "longitude": float(reg.longitude),
            "distancia_metros": distancia,
            "fora_do_raio": fora_do_raio,
            "titulo": titulo,
            "subtitulo": subtitulo,
        })

    return {
        "registros": linha_do_tempo,
        "total_registros": len(linha_do_tempo),
        "total_saidas_raio": total_saidas_raio,
        "centro_mapa": {
            "latitude": float(endereco_base.latitude) if endereco_base else None,
            "longitude": float(endereco_base.longitude) if endereco_base else None,
            "raio_metros": raio_seguro_metros,
        }
    }