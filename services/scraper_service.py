from datetime import datetime

from agent.prompts.cv import obtener_nombre_cv_linkedin
from scraper.linkedin.jobs_scraper import extraer_ofertas
from scraper.linkedin.easy_apply_scraper import (
    extraer_preguntas,
    SolicitudNoDisponibleError,
)
from scraper.linkedin.apply import enviar_solicitud
from database import SessionLocal
from models import Estado
from repositories import oferta_repository
from services.retry import ejecutar_con_reintentos
from services.oferta_service import marcar_error_oferta


class OfertaNoEncontradaError(ValueError):
    pass


class OfertaNoListaParaAplicarError(ValueError):
    pass


class CvLinkedInNoConfiguradoError(ValueError):
    pass


def ejecutar_scraper_linkedin(busqueda: str):
    try:
        ofertas = ejecutar_con_reintentos(
            lambda: extraer_ofertas(busqueda),
            "el scraper de ofertas de LinkedIn",
        )

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
            preguntas = ejecutar_con_reintentos(
                lambda: extraer_preguntas(oferta.url),
                "el scraper de preguntas de Easy Apply",
                no_reintentar=(SolicitudNoDisponibleError,),
            )

        except SolicitudNoDisponibleError as error:
            marcar_error_oferta(db, id)

            return {
                "oferta_id": id,
                "disponible": False,
                "oferta_eliminada": False,
                "error": str(error),
            }
        except Exception as error:
            marcar_error_oferta(db, id)
            raise

        estado_final = (
            Estado.PENDIENTE_RESPUESTAS
            if preguntas
            else Estado.LISTA_PARA_APLICAR
        )

        # Los selectores pertenecen a la sesión de Playwright que los generó.
        # Se devuelven para diagnóstico, pero no se almacenan porque no son
        # reutilizables en una sesión posterior.
        preguntas_persistibles = [
            {
                clave: valor
                for clave, valor in pregunta.items()
                if clave != "selector_temporal"
            }
            for pregunta in preguntas
        ]

        resultado = oferta_repository.modificar_datos_oferta(
            db,
            id,
            {
                "preguntas_formulario": preguntas_persistibles,
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


def ejecutar_aplicacion_easy_apply(id: str):
    """Envía una oferta que ya ha sido revisada y está lista para aplicar."""
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)

        if oferta is None or oferta.eliminado:
            raise OfertaNoEncontradaError("Oferta no encontrada")

        if not oferta.aplicacion_sencilla or oferta.plataforma.lower() != "linkedin":
            raise OfertaNoListaParaAplicarError(
                "La oferta no admite Easy Apply de LinkedIn"
            )

        if oferta.estado != Estado.LISTA_PARA_APLICAR:
            raise OfertaNoListaParaAplicarError(
                "La oferta debe estar en estado lista_para_aplicar"
            )

        preguntas = oferta.preguntas_formulario or []
        respuestas = oferta.respuestas_formulario or []
        _validar_respuestas_para_envio(preguntas, respuestas)

        try:
            nombre_cv = obtener_nombre_cv_linkedin(
                oferta.perfil_recomendado.value,
                oferta.idioma_oferta,
            )
        except (AttributeError, ValueError) as error:
            raise CvLinkedInNoConfiguradoError(
                "No hay un CV de LinkedIn configurado para el perfil e idioma "
                "de esta oferta"
            ) from error

        resultado = enviar_solicitud(oferta.url, preguntas, respuestas, nombre_cv)

        oferta_repository.modificar_datos_oferta(
            db,
            id,
            {
                "estado": Estado.APLICADA,
                "fecha_aplicacion": datetime.now(),
            },
        )

        return {
            "oferta_id": id,
            **resultado,
            "estado": Estado.APLICADA.value,
        }


def _validar_respuestas_para_envio(
    preguntas: list[dict],
    respuestas: list[dict],
) -> None:
    respuestas_por_id = {
        respuesta.get("pregunta_id"): respuesta for respuesta in respuestas
    }

    for pregunta in preguntas:
        if not pregunta.get("obligatoria"):
            continue

        respuesta = respuestas_por_id.get(pregunta["pregunta_id"])
        if respuesta is None or not respuesta.get("informacion_suficiente"):
            raise OfertaNoListaParaAplicarError(
                "Hay preguntas obligatorias sin una respuesta revisada"
            )

        if pregunta["tipo"] in {"radio", "select"}:
            if respuesta.get("valor_seleccionado") is None:
                raise OfertaNoListaParaAplicarError(
                    "Hay preguntas de selección sin un valor revisado"
                )
        elif not respuesta.get("respuesta"):
            raise OfertaNoListaParaAplicarError(
                "Hay preguntas de texto sin una respuesta revisada"
            )
