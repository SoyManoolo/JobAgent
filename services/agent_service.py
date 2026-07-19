from models import Estado
from agent import llm
from repositories import oferta_repository
from database import SessionLocal
from agent.prompts.cv import obtener_cv


def validar_respuestas_formulario(
    preguntas: list[dict], resultado: dict
) -> bool:
    """Valida las respuestas y devuelve si todas las obligatorias están resueltas."""
    respuestas = resultado.get("respuestas")

    if not isinstance(respuestas, list):
        raise ValueError("El resultado del LLM no contiene una lista de respuestas")

    preguntas_ids = [pregunta["pregunta_id"] for pregunta in preguntas]
    respuestas_ids = [respuesta.get("pregunta_id") for respuesta in respuestas]

    if len(respuestas_ids) != len(set(respuestas_ids)):
        raise ValueError("El LLM ha devuelto identificadores de pregunta duplicados")

    if set(respuestas_ids) != set(preguntas_ids):
        raise ValueError(
            "Los identificadores de las respuestas no coinciden con las preguntas"
        )

    preguntas_por_id = {
        pregunta["pregunta_id"]: pregunta for pregunta in preguntas
    }
    todas_obligatorias_resueltas = True

    for respuesta in respuestas:
        pregunta = preguntas_por_id[respuesta["pregunta_id"]]

        if not isinstance(respuesta.get("informacion_suficiente"), bool):
            raise ValueError("informacion_suficiente debe ser un booleano")

        informacion_suficiente = respuesta["informacion_suficiente"]
        texto_respuesta = respuesta.get("respuesta")
        valor_seleccionado = respuesta.get("valor_seleccionado")

        if not informacion_suficiente:
            if texto_respuesta is not None or valor_seleccionado is not None:
                raise ValueError(
                    "Una respuesta sin información suficiente debe contener valores nulos"
                )
            if pregunta["obligatoria"]:
                todas_obligatorias_resueltas = False
            continue

        if not isinstance(texto_respuesta, str) or not texto_respuesta.strip():
            raise ValueError("Una respuesta suficiente debe incluir texto")

        if pregunta["tipo"] in {"radio", "select"}:
            valores_opciones = {
                opcion["valor"] for opcion in pregunta["opciones"]
            }
            if valor_seleccionado not in valores_opciones:
                raise ValueError(
                    "valor_seleccionado no coincide con una opción de la pregunta"
                )
        elif valor_seleccionado is not None:
            raise ValueError(
                "Las preguntas de texto o número no deben tener valor_seleccionado"
            )

    return todas_obligatorias_resueltas


def procesar_ofertas_extraidas():
    with SessionLocal() as db:
        ofertas = oferta_repository.obtener_ofertas_estado(
            db, estado=Estado.EXTRAIDA, limite=25
        )

        total = len(ofertas)
        procesadas = 0
        errores = 0

        for oferta in ofertas:
            try:
                resultado = llm.analizar_oferta(oferta.descripcion)

                print("Resultado: ", resultado)

                if (
                    resultado["idioma"] == "otro"
                    or resultado["score_encaje"] < 20
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

                oferta_repository.modificar_datos_oferta(
                    db, oferta.id, datos_actualizar
                )
                procesadas += 1

            except Exception as e:
                print(f"Error procesando la oferta {oferta.id}: {e}")

                oferta_repository.modificar_datos_oferta(
                    db, oferta.id, {"estado": Estado.ERROR}
                )

                errores += 1
            continue

    return {"total": total, "procesadas": procesadas, "errores": errores}


def responder_preguntas_oferta(id: str):
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)
        if not oferta:
            return {"error": "Oferta no encontrada"}

        try:
            cv = obtener_cv(
                oferta.perfil_recomendado.value,
                oferta.idioma_oferta,
            )
            respuestas = llm.responder_preguntas_oferta(oferta.descripcion, cv, preguntas=oferta.preguntas_formulario)
            lista_para_aplicar = validar_respuestas_formulario(
                oferta.preguntas_formulario,
                respuestas,
            )

            oferta_repository.modificar_datos_oferta(
                db,
                oferta.id,
                {
                    "respuestas_formulario": respuestas["respuestas"],
                    "estado": (
                        Estado.LISTA_PARA_APLICAR
                        if lista_para_aplicar
                        else Estado.PENDIENTE_RESPUESTAS
                    ),
                },
            )
            return {"respuestas": respuestas}
        except Exception as e:
            print(f"Error respondiendo preguntas para la oferta {id}: {e}")
            return {"error": "Error al procesar la solicitud"}


def responder_preguntas_ofertas():
    with SessionLocal() as db:
        ofertas = oferta_repository.obtener_ofertas_estado(
            db, estado=Estado.PENDIENTE_RESPUESTAS, limite=25
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
                lista_para_aplicar = validar_respuestas_formulario(
                    oferta.preguntas_formulario,
                    respuestas,
                )
                print(f"Respuestas para la oferta {oferta.id}: {respuestas}")
                procesadas += 1

                oferta_repository.modificar_datos_oferta(
                    db,
                oferta.id,
                    {
                        "respuestas_formulario": respuestas["respuestas"],
                        "estado": (
                            Estado.LISTA_PARA_APLICAR
                            if lista_para_aplicar
                            else Estado.PENDIENTE_RESPUESTAS
                        ),
                    },
                )
            except Exception as e:
                print(f"Error respondiendo preguntas para la oferta {oferta.id}: {e}")
                errores += 1
            continue

    return {"total": total, "procesadas": procesadas, "errores": errores}
