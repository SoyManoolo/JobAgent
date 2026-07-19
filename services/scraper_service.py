from scraper.linkedin.jobs_scraper import extraer_ofertas
from scraper.linkedin.easy_apply_scraper import (
    extraer_preguntas,
    SolicitudNoDisponibleError,
)
from database import SessionLocal
from models import Estado
from repositories import oferta_repository


def ejecutar_scraper_linkedin(busqueda: str):
    try:
        ofertas = extraer_ofertas(busqueda)

        with SessionLocal() as db:
            resultado = oferta_repository.guardar_ofertas(db, ofertas)
            return {
                "busqueda": busqueda,
                "ofertas_extraidas": len(ofertas),
                **resultado,
            }
    except Exception as e:
        print(f"Error ejecutando scraper: {e}", flush=True)
        raise


def ejecutar_scraper_preguntas_linkedin(id: str):
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)

        if oferta is None:
            raise ValueError("Oferta no encontrada")

        if not oferta.aplicacion_sencilla:
            raise ValueError("La oferta no tiene solicitud sencilla")

        try:
            preguntas = extraer_preguntas(oferta.url)

        except SolicitudNoDisponibleError:
            eliminada = oferta_repository.eliminar_oferta(db, id)

            return {
                "oferta_id": id,
                "disponible": False,
                "oferta_eliminada": bool(eliminada),
            }

        estado_final = (
            Estado.PENDIENTE_RESPUESTAS
            if preguntas
            else Estado.LISTA_PARA_APLICAR
        )

        resultado = oferta_repository.modificar_datos_oferta(
            db,
            id,
            {
                "preguntas_formulario": preguntas,
                "estado": estado_final,
            },
        )

        return {
            "oferta_id": id,
            "disponible": True,
            "total_preguntas": len(preguntas),
            "preguntas": preguntas,
            "actualizada": resultado is not None,
        }


def ejecutar_scraper_preguntas_pendientes(limite: int = 10):
    with SessionLocal() as db:
        ofertas = oferta_repository.obtener_ofertas_para_extraer_preguntas(
            db,
            limite=limite,
        )

    resultados = []

    for oferta in ofertas:
        try:
            resultado = ejecutar_scraper_preguntas_linkedin(oferta.id)
            resultados.append(resultado)
        except Exception as error:
            resultados.append(
                {
                    "oferta_id": oferta.id,
                    "error": str(error),
                }
            )

    return {
        "total": len(ofertas),
        "resultados": resultados,
    }
