from typing import Optional
from database import SessionLocal
from repositories import oferta_repository
from models.oferta import Estado, PerfilRecomendado


class RespuestaFormularioError(ValueError):
    pass


def obtener_oferta_id(id):
    with SessionLocal() as db:
        return oferta_repository.obtener_oferta_id(db, id)


def obtener_ofertas(
    pagina: int,
    limite: int,
    estado: Optional[Estado] = None,
    perfil: Optional[PerfilRecomendado] = None,
    score_min: Optional[int] = None,
    empresa: Optional[str] = None,
    aplicacion_sencilla: Optional[bool] = None,
):
    with SessionLocal() as db:
        ofertas, total = oferta_repository.devolver_ofertas(
            db, pagina, limite, estado, perfil, score_min, empresa, aplicacion_sencilla
        )
    return {"total": total, "pagina": pagina, "limite": limite, "resultados": ofertas}


def eliminar_oferta(id):
    with SessionLocal() as db:
        return oferta_repository.eliminar_oferta(db, id)


def modificar_oferta(id, datos):
    with SessionLocal() as db:
        return oferta_repository.modificar_datos_oferta(db, id, datos)


def editar_respuesta_formulario(id: str, pregunta_id: str, datos):
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)
        if not oferta or oferta.eliminado:
            return None

        preguntas = oferta.preguntas_formulario or []
        pregunta = next(
            (item for item in preguntas if item["pregunta_id"] == pregunta_id),
            None,
        )
        if pregunta is None:
            raise RespuestaFormularioError("La pregunta no pertenece a la oferta")

        respuestas = oferta.respuestas_formulario or []
        respuesta_actual = next(
            (item for item in respuestas if item.get("pregunta_id") == pregunta_id),
            {"pregunta_id": pregunta_id},
        ).copy()
        campos = datos.model_fields_set

        if pregunta["tipo"] in {"radio", "select"}:
            if "valor_seleccionado" not in campos:
                raise RespuestaFormularioError(
                    "Las preguntas de selección requieren valor_seleccionado"
                )

            valor = datos.valor_seleccionado
            if valor is None:
                respuesta_actual.update(
                    respuesta=None,
                    valor_seleccionado=None,
                    informacion_suficiente=False,
                )
            else:
                opcion = next(
                    (item for item in pregunta["opciones"] if item["valor"] == valor),
                    None,
                )
                if opcion is None:
                    raise RespuestaFormularioError(
                        "valor_seleccionado no coincide con una opción válida"
                    )
                respuesta_actual.update(
                    respuesta=opcion["texto"],
                    valor_seleccionado=valor,
                    informacion_suficiente=True,
                )
        else:
            if "valor_seleccionado" in campos and datos.valor_seleccionado is not None:
                raise RespuestaFormularioError(
                    "Las preguntas de texto o número no admiten valor_seleccionado"
                )
            if "respuesta" not in campos:
                raise RespuestaFormularioError(
                    "Las preguntas de texto o número requieren respuesta"
                )

            texto = datos.respuesta.strip() if datos.respuesta else None
            respuesta_actual.update(
                respuesta=texto,
                valor_seleccionado=None,
                informacion_suficiente=bool(texto),
            )

        respuestas_actualizadas = [
            item for item in respuestas if item.get("pregunta_id") != pregunta_id
        ]
        respuestas_actualizadas.append(respuesta_actual)
        oferta_repository.modificar_datos_oferta(
            db, id, {"respuestas_formulario": respuestas_actualizadas}
        )

        return {
            "respuesta": respuesta_actual,
            "todas_obligatorias_resueltas": _obligatorias_resueltas(
                preguntas, respuestas_actualizadas
            ),
            "estado": oferta.estado.value,
        }


def confirmar_respuestas_formulario(id: str):
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)
        if not oferta or oferta.eliminado:
            return None

        if oferta.estado != Estado.PENDIENTE_RESPUESTAS:
            raise RespuestaFormularioError(
                "La oferta debe estar en estado pendientes_respuestas"
            )

        preguntas = oferta.preguntas_formulario or []
        respuestas = oferta.respuestas_formulario or []
        if not _obligatorias_resueltas(preguntas, respuestas):
            raise RespuestaFormularioError(
                "Hay preguntas obligatorias sin una respuesta válida"
            )

        return oferta_repository.modificar_datos_oferta(
            db, id, {"estado": Estado.LISTA_PARA_APLICAR}
        )


def _obligatorias_resueltas(preguntas: list[dict], respuestas: list[dict]) -> bool:
    respuestas_por_id = {item.get("pregunta_id"): item for item in respuestas}

    for pregunta in preguntas:
        if not pregunta.get("obligatoria"):
            continue
        respuesta = respuestas_por_id.get(pregunta["pregunta_id"])
        if respuesta is None or not respuesta.get("informacion_suficiente"):
            return False
        if pregunta["tipo"] in {"radio", "select"}:
            valores = {opcion["valor"] for opcion in pregunta["opciones"]}
            if respuesta.get("valor_seleccionado") not in valores:
                return False
        elif not isinstance(respuesta.get("respuesta"), str) or not respuesta["respuesta"].strip():
            return False

    return True
