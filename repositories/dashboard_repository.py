from sqlalchemy import func
from sqlalchemy.orm import Session

from models.oferta import Estado, Oferta, PerfilRecomendado


def obtener_stats(db: Session):
    """Devuelve las agregaciones de ofertas necesarias para el dashboard."""
    query_base = db.query(Oferta).filter(Oferta.eliminado.is_(False))

    total = query_base.count()

    estados = {estado.value: 0 for estado in Estado}
    for estado, cantidad in query_base.with_entities(
        Oferta.estado, func.count(Oferta.id)
    ).group_by(Oferta.estado):
        estados[estado.value] = cantidad

    perfiles = {
        PerfilRecomendado.BACKEND.value: 0,
        PerfilRecomendado.IA.value: 0,
        PerfilRecomendado.DESCONOCIDO.value: 0,
        "sin_clasificar": 0,
    }
    for perfil, cantidad in query_base.with_entities(
        Oferta.perfil_recomendado, func.count(Oferta.id)
    ).group_by(Oferta.perfil_recomendado):
        clave = perfil.value if perfil is not None else "sin_clasificar"
        perfiles[clave] = cantidad

    plataformas = {
        plataforma: cantidad
        for plataforma, cantidad in query_base.with_entities(
            Oferta.plataforma, func.count(Oferta.id)
        ).group_by(Oferta.plataforma)
    }

    query_scores = query_base.filter(Oferta.score_encaje.is_not(None))
    total_scores, score_medio, score_minimo, score_maximo = query_scores.with_entities(
        func.count(Oferta.id),
        func.avg(Oferta.score_encaje),
        func.min(Oferta.score_encaje),
        func.max(Oferta.score_encaje),
    ).one()

    rangos_score = {
        "0_19": query_scores.filter(Oferta.score_encaje.between(0, 19)).count(),
        "20_39": query_scores.filter(Oferta.score_encaje.between(20, 39)).count(),
        "40_59": query_scores.filter(Oferta.score_encaje.between(40, 59)).count(),
        "60_79": query_scores.filter(Oferta.score_encaje.between(60, 79)).count(),
        "80_100": query_scores.filter(Oferta.score_encaje.between(80, 100)).count(),
    }

    ofertas_prioritarias = query_base.filter(
        Oferta.estado.in_(
            [
                Estado.ANALIZADA,
                Estado.PENDIENTE_RESPUESTAS,
                Estado.LISTA_PARA_APLICAR,
            ]
        ),
        Oferta.score_encaje >= 70,
    ).count()

    easy_apply = query_base.filter(Oferta.aplicacion_sencilla.is_(True))
    aplicadas = estados[Estado.APLICADA.value]

    return {
        "total_ofertas": total,
        "aplicadas": aplicadas,
        "descartadas": estados[Estado.DESCARTADA.value],
        "por_estado": estados,
        "pendientes": {
            "analisis": estados[Estado.EXTRAIDA.value],
            "respuestas": estados[Estado.PENDIENTE_RESPUESTAS.value],
            "listas_para_aplicar": estados[Estado.LISTA_PARA_APLICAR.value],
        },
        "ofertas_prioritarias": {
            "score_minimo": 70,
            "total": ofertas_prioritarias,
        },
        "score_encaje": {
            "ofertas_evaluadas": total_scores,
            "medio": round(float(score_medio), 2) if score_medio is not None else None,
            "minimo": score_minimo,
            "maximo": score_maximo,
            "por_rango": rangos_score,
        },
        "easy_apply": {
            "total": easy_apply.count(),
            "pendientes_preguntas": easy_apply.filter(
                Oferta.estado == Estado.ANALIZADA,
                Oferta.preguntas_formulario.is_(None),
            ).count(),
            "pendientes_respuestas": easy_apply.filter(
                Oferta.estado == Estado.PENDIENTE_RESPUESTAS
            ).count(),
            "listas_para_aplicar": easy_apply.filter(
                Oferta.estado == Estado.LISTA_PARA_APLICAR
            ).count(),
        },
        "por_perfil": perfiles,
        "por_plataforma": plataformas,
        "tasa_aplicacion": round((aplicadas / total) * 100, 2) if total else 0,
    }
