import json
from functools import wraps
from threading import Lock

import requests

from models import Estado
from agent import llm
from repositories import oferta_repository
from database import SessionLocal
from agent.prompts.cv import obtener_cv
from services.oferta_service import marcar_error_oferta


class RespuestaFormularioError(ValueError):
    pass


class OllamaNoDisponibleError(RuntimeError):
    """Ollama no respondió correctamente tras los reintentos."""


class RespuestaOllamaInvalidaError(ValueError):
    """Ollama respondió, pero su contenido no cumple el contrato esperado."""


class AnalisisEnCursoError(RuntimeError):
    """Ya hay una ejecución de análisis de ofertas usando Ollama."""


class OllamaEnUsoError(RuntimeError):
    """Otra operación ya está usando Ollama."""


_bloqueo_analisis = Lock()
_bloqueo_ollama = Lock()


def _adquirir_bloqueo_analisis() -> None:
    if not _bloqueo_analisis.acquire(blocking=False):
        raise AnalisisEnCursoError("Ya hay un análisis de ofertas en curso")


def _requiere_ollama(funcion):
    """Evita inferencias concurrentes contra la única instancia de Ollama."""
    @wraps(funcion)
    def envuelta(*args, **kwargs):
        if not _bloqueo_ollama.acquire(blocking=False):
            raise OllamaEnUsoError("Ollama ya está procesando otra tarea")
        try:
            return funcion(*args, **kwargs)
        finally:
            _bloqueo_ollama.release()

    return envuelta


def _marca_error_respuestas(funcion):
    """Registra el fallo de una generación individual para revisión manual."""
    @wraps(funcion)
    def envuelta(id: str, *args, **kwargs):
        try:
            return funcion(id, *args, **kwargs)
        except Exception as error:
            with SessionLocal() as db:
                if oferta_repository.obtener_oferta_id(db, id) is not None:
                    marcar_error_oferta(db, id)
            raise

    return envuelta


def normalizar_respuestas_formulario(
    preguntas: list[dict], resultado: dict
) -> dict:
    """Asocia por posición las respuestas del LLM con los IDs persistidos.

    Los identificadores de LinkedIn son largos y no aportan contexto al modelo.
    Por ello no se le pide que los reproduzca: el backend conserva los originales
    y también normaliza el texto de las opciones seleccionadas.
    """
    respuestas = resultado.get("respuestas")
    if not isinstance(respuestas, list):
        raise ValueError("El resultado del LLM no contiene una lista de respuestas")
    if len(respuestas) != len(preguntas):
        raise ValueError(
            "El número de respuestas del LLM no coincide con las preguntas"
        )

    respuestas_normalizadas = []
    for pregunta, respuesta in zip(preguntas, respuestas):
        if not isinstance(respuesta, dict):
            raise ValueError("Cada respuesta del LLM debe ser un objeto JSON")

        normalizada = {
            "pregunta_id": pregunta["pregunta_id"],
            "respuesta": respuesta.get("respuesta"),
            "valor_seleccionado": respuesta.get("valor_seleccionado"),
            "informacion_suficiente": respuesta.get("informacion_suficiente"),
        }

        if (
            pregunta["tipo"] in {"radio", "select"}
            and normalizada["informacion_suficiente"] is True
        ):
            opcion = next(
                (
                    item
                    for item in pregunta["opciones"]
                    if item["valor"] == normalizada["valor_seleccionado"]
                ),
                None,
            )
            if opcion is not None:
                normalizada["respuesta"] = opcion["texto"]

        respuestas_normalizadas.append(normalizada)

    return {"respuestas": respuestas_normalizadas}


def _imprimir_error_validacion_respuesta(
    pregunta: dict, respuesta: dict, motivo: str
) -> None:
    """Muestra el contexto mínimo necesario para diagnosticar una respuesta inválida."""
    print(
        "Validación rechazada de respuesta de Ollama: "
        + json.dumps(
            {
                "motivo": motivo,
                "pregunta": {
                    "pregunta_id": pregunta.get("pregunta_id"),
                    "texto": pregunta.get("texto"),
                    "tipo": pregunta.get("tipo"),
                    "obligatoria": pregunta.get("obligatoria"),
                    "opciones": pregunta.get("opciones"),
                },
                "respuesta_normalizada": respuesta,
            },
            ensure_ascii=False,
            default=str,
        ),
        flush=True,
    )


def validar_respuestas_formulario(
    preguntas: list[dict], resultado: dict
) -> bool:
    """Valida las respuestas y devuelve si todas las obligatorias están resueltas."""
    respuestas = resultado.get("respuestas")

    if not isinstance(respuestas, list):
        raise ValueError("El resultado del LLM no contiene una lista de respuestas")

    preguntas_por_id = {
        pregunta["pregunta_id"]: pregunta for pregunta in preguntas
    }
    todas_obligatorias_resueltas = True

    for respuesta in respuestas:
        pregunta = preguntas_por_id[respuesta["pregunta_id"]]

        if not isinstance(respuesta.get("informacion_suficiente"), bool):
            _imprimir_error_validacion_respuesta(
                pregunta, respuesta, "informacion_suficiente no es booleano"
            )
            raise ValueError("informacion_suficiente debe ser un booleano")

        informacion_suficiente = respuesta["informacion_suficiente"]
        texto_respuesta = respuesta.get("respuesta")
        valor_seleccionado = respuesta.get("valor_seleccionado")

        if not informacion_suficiente:
            if texto_respuesta is not None or valor_seleccionado is not None:
                _imprimir_error_validacion_respuesta(
                    pregunta,
                    respuesta,
                    "informacion_suficiente=false con respuesta o valor_seleccionado no nulo",
                )
                raise ValueError(
                    "Una respuesta sin información suficiente debe contener valores nulos"
                )
            if pregunta["obligatoria"]:
                todas_obligatorias_resueltas = False
            continue

        if not isinstance(texto_respuesta, str) or not texto_respuesta.strip():
            _imprimir_error_validacion_respuesta(
                pregunta, respuesta, "informacion_suficiente=true sin texto de respuesta"
            )
            raise ValueError("Una respuesta suficiente debe incluir texto")

        if pregunta["tipo"] in {"radio", "select"}:
            valores_opciones = {
                opcion["valor"] for opcion in pregunta["opciones"]
            }
            if valor_seleccionado not in valores_opciones:
                _imprimir_error_validacion_respuesta(
                    pregunta,
                    respuesta,
                    "valor_seleccionado no coincide con las opciones disponibles",
                )
                raise ValueError(
                    "valor_seleccionado no coincide con una opción de la pregunta"
                )
        elif valor_seleccionado is not None:
            _imprimir_error_validacion_respuesta(
                pregunta,
                respuesta,
                "pregunta de texto o número con valor_seleccionado no nulo",
            )
            raise ValueError(
                "Las preguntas de texto o número no deben tener valor_seleccionado"
            )

    return todas_obligatorias_resueltas


def _analizar_oferta(db, oferta):
    """Analiza una oferta y persiste el resultado de la clasificación."""
    resultado = llm.analizar_oferta(oferta.descripcion)

    if (
        resultado["idioma"] == "otro"
        or resultado["score_encaje"] < 35
        or resultado["perfil_recomendado"] == "desconocido"
    ):
        estado_final = Estado.DESCARTADA
    else:
        estado_final = Estado.ANALIZADA

    datos_actualizar = {
        "perfil_recomendado": resultado["perfil_recomendado"],
        "idioma_oferta": resultado["idioma"],
        "seniority": resultado["seniority"],
        "score_backend": resultado["score_backend"],
        "score_ia": resultado["score_ia"],
        "score_encaje": resultado["score_encaje"],
        "resumen": resultado["resumen"],
        "motivo_encaje": resultado["motivo_encaje"],
        "estado": estado_final,
    }

    return oferta_repository.modificar_datos_oferta(db, oferta.id, datos_actualizar)


@_requiere_ollama
def procesar_oferta(id: str):
    """Analiza una única oferta activa identificada por su UUID.

    Si el análisis falla, la oferta queda marcada como ``error`` y se propaga
    la excepción para que la ruta responda con un error HTTP.
    """
    _adquirir_bloqueo_analisis()
    try:
        with SessionLocal() as db:
            oferta = oferta_repository.obtener_oferta_id(db, id)

            if not oferta or oferta.eliminado:
                return None

            try:
                return _analizar_oferta(db, oferta)
            except Exception as error:
                marcar_error_oferta(db, oferta.id)
                raise
    finally:
        _bloqueo_analisis.release()


@_requiere_ollama
def procesar_ofertas_extraidas(limite: int = 25):
    _adquirir_bloqueo_analisis()
    try:
        with SessionLocal() as db:
            ofertas = oferta_repository.obtener_ofertas_estado(
                db, estado=Estado.EXTRAIDA, limite=limite
            )

            total = len(ofertas)
            procesadas = 0
            errores = 0

            for oferta in ofertas:
                try:
                    _analizar_oferta(db, oferta)
                    procesadas += 1
                except Exception as e:
                    print(f"Error procesando la oferta {oferta.id}: {e}")
                    marcar_error_oferta(db, oferta.id)
                    errores += 1

        return {"total": total, "procesadas": procesadas, "errores": errores}
    finally:
        _bloqueo_analisis.release()


@_requiere_ollama
@_marca_error_respuestas
def responder_preguntas_oferta(id: str):
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)
        if not oferta:
            return None

        try:
            cv = obtener_cv(
                oferta.perfil_recomendado.value,
                oferta.idioma_oferta,
            )
        except (AttributeError, ValueError) as error:
            raise RespuestaFormularioError(
                "La oferta no tiene un perfil e idioma válidos para elegir el CV"
            ) from error

        # No se retiene una conexión SQLite durante la inferencia de Ollama.
        descripcion = oferta.descripcion
        preguntas = oferta.preguntas_formulario

    try:
        respuestas = llm.responder_preguntas_oferta(
            descripcion,
            cv,
            preguntas=preguntas,
        )
    except requests.RequestException as error:
        print(
            f"Ollama no respondió al generar respuestas para {id}: {error}",
            flush=True,
        )
        raise OllamaNoDisponibleError(
            "Ollama no respondió después de los reintentos"
        ) from error
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(
            f"Ollama devolvió una respuesta no válida para {id}: {error}",
            flush=True,
        )
        raise RespuestaOllamaInvalidaError(
            "Ollama devolvió una respuesta con un formato no válido"
        ) from error

    try:
        respuestas = normalizar_respuestas_formulario(preguntas, respuestas)
        todas_obligatorias_resueltas = validar_respuestas_formulario(
            preguntas,
            respuestas,
        )
    except ValueError as error:
        print(
            "Respuesta de Ollama rechazada para la oferta "
            f"{id}: {error}",
            flush=True,
        )
        raise RespuestaOllamaInvalidaError(str(error)) from error

    estado_final = (
        Estado.LISTA_PARA_APLICAR
        if todas_obligatorias_resueltas
        else Estado.PENDIENTE_RESPUESTAS
    )
    with SessionLocal() as db:
        oferta_actualizada = oferta_repository.modificar_datos_oferta(
            db,
            id,
            {
                "respuestas_formulario": respuestas["respuestas"],
                "estado": estado_final,
            },
        )

    if oferta_actualizada is None:
        return None

    return {"respuestas": respuestas, "estado": estado_final.value}


@_requiere_ollama
def responder_preguntas_ofertas(limite: int = 5):
    with SessionLocal() as db:
        ofertas = oferta_repository.obtener_ofertas_estado(
            db, estado=Estado.PENDIENTE_RESPUESTAS, limite=limite
        )

        total = len(ofertas)
        procesadas = 0
        errores = 0

        for oferta in ofertas:
            try:
                cv = obtener_cv(
                    oferta.perfil_recomendado.value,
                    oferta.idioma_oferta,
                )

                respuestas = llm.responder_preguntas_oferta(oferta.descripcion, cv, preguntas=oferta.preguntas_formulario)
                respuestas = normalizar_respuestas_formulario(
                    oferta.preguntas_formulario,
                    respuestas,
                )
                todas_obligatorias_resueltas = validar_respuestas_formulario(
                    oferta.preguntas_formulario,
                    respuestas,
                )
                procesadas += 1

                oferta_repository.modificar_datos_oferta(
                    db,
                    oferta.id,
                    {
                        "respuestas_formulario": respuestas["respuestas"],
                        "estado": (
                            Estado.LISTA_PARA_APLICAR
                            if todas_obligatorias_resueltas
                            else Estado.PENDIENTE_RESPUESTAS
                        ),
                    },
                )
            except Exception as e:
                print(f"Error respondiendo preguntas para la oferta {oferta.id}: {e}")
                marcar_error_oferta(db, oferta.id)
                errores += 1
            continue

    return {"total": total, "procesadas": procesadas, "errores": errores}
