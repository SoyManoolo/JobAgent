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


# Excepciones personalizadas para errores específicos relacionados con la ejecución del scraper y la aplicación a ofertas de trabajo.
class OfertaNoEncontradaError(ValueError):
    pass


class OfertaNoListaParaAplicarError(ValueError):
    pass


class EstadoOfertaNoValidoError(ValueError):
    pass


class CvLinkedInNoConfiguradoError(ValueError):
    pass


# Función que ejecuta el scraper de LinkedIn para extraer ofertas de trabajo basadas en una búsqueda específica. Se utiliza la función `ejecutar_con_reintentos` para manejar posibles fallos temporales durante la extracción de ofertas
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


# Función que ejecuta el scraper de LinkedIn para extraer las preguntas de un formulario asociado a una oferta específica
def ejecutar_scraper_preguntas_linkedin(id: str):
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)

        if oferta is None or oferta.eliminado:
            raise OfertaNoEncontradaError("Oferta no encontrada")

        if oferta.estado != Estado.ANALIZADA:
            raise EstadoOfertaNoValidoError(
                "La oferta debe estar en estado analizada para extraer preguntas"
            )

        if not oferta.aplicacion_sencilla:
            raise ValueError("La oferta no tiene solicitud sencilla")

        url = oferta.url

    def actualizar_si_analizada(datos):
        with SessionLocal() as db:
            if oferta_repository.modificar_si_estado(db, id, Estado.ANALIZADA, datos):
                return
            actual = oferta_repository.obtener_oferta_id(db, id)
            if actual is None or actual.eliminado:
                raise OfertaNoEncontradaError("Oferta no encontrada")
            raise EstadoOfertaNoValidoError(
                "La oferta debe estar en estado analizada para extraer preguntas"
            )

    # La navegación no conserva una sesión de base de datos abierta.
    try:
        preguntas = ejecutar_con_reintentos(
            lambda: extraer_preguntas(url),
            "el scraper de preguntas de Easy Apply",
            no_reintentar=(SolicitudNoDisponibleError,),
        )

    except SolicitudNoDisponibleError as error:
        actualizar_si_analizada({"estado": Estado.ERROR})
        return {
            "oferta_id": id,
            "disponible": False,
            "oferta_eliminada": False,
            "error": str(error),
        }
    except Exception:
        actualizar_si_analizada({"estado": Estado.ERROR})
        raise

    estado_final = Estado.PENDIENTE_RESPUESTAS if preguntas else Estado.LISTA_PARA_APLICAR
    # Los selectores de Playwright no son reutilizables en otra sesión.
    preguntas_persistibles = [
        {clave: valor for clave, valor in pregunta.items() if clave != "selector_temporal"}
        for pregunta in preguntas
    ]

    actualizar_si_analizada({
        "preguntas_formulario": preguntas_persistibles,
        "estado": estado_final,
    })

    return {
        "oferta_id": id,
        "disponible": True,
        "total_preguntas": len(preguntas),
        "preguntas": preguntas,
        "actualizada": True,
    }


# Función que ejecuta el scraper de LinkedIn para extraer las preguntas de varias ofertas pendientes de respuesta, hasta un límite especificado
def ejecutar_scraper_preguntas_pendientes(limite: int = 10):
    with SessionLocal() as db:
        ofertas = oferta_repository.obtener_ofertas_para_extraer_preguntas(
            db,
            limite=limite,
        )

    resultados = []

    # Ejecutar el scraper de preguntas para cada oferta
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


# Función que ejecuta la aplicación a una oferta de trabajo utilizando el método Easy Apply de LinkedIn
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

        # Validar que todas las preguntas obligatorias tengan respuestas revisadas antes de enviar la solicitud
        preguntas = oferta.preguntas_formulario or []
        respuestas = oferta.respuestas_formulario or []
        _validar_respuestas_para_envio(preguntas, respuestas)

        # Obtener el nombre del CV de LinkedIn configurado para el perfil e idioma de la oferta. Si no hay un CV configurado, se lanza una excepción específica.
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

        if not oferta_repository.modificar_si_estado(
            db, id, Estado.LISTA_PARA_APLICAR,
            {
                "estado": Estado.APLICADA,
                "fecha_aplicacion": datetime.now(),
            },
        ):
            raise OfertaNoListaParaAplicarError(
                "La oferta debe seguir activa y en estado lista_para_aplicar"
            )

        return {
            "oferta_id": id,
            **resultado,
            "estado": Estado.APLICADA.value,
        }


# Función que valida que todas las preguntas obligatorias de un formulario tengan respuestas revisadas antes de enviar la solicitud
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

        # Validar que la pregunta obligatoria tenga una respuesta revisada
        respuesta = respuestas_por_id.get(pregunta["pregunta_id"])
        if respuesta is None or not respuesta.get("informacion_suficiente"):
            raise OfertaNoListaParaAplicarError(
                "Hay preguntas obligatorias sin una respuesta revisada"
            )

        # Validar que las preguntas de selección tengan un valor seleccionado y que las preguntas de texto tengan una respuesta revisada
        if pregunta["tipo"] in {"radio", "select"}:
            if respuesta.get("valor_seleccionado") is None:
                raise OfertaNoListaParaAplicarError(
                    "Hay preguntas de selección sin un valor revisado"
                )
        elif not respuesta.get("respuesta"):
            raise OfertaNoListaParaAplicarError(
                "Hay preguntas de texto sin una respuesta revisada"
            )
