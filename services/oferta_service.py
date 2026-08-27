from typing import Optional
from database import SessionLocal
from repositories import oferta_repository
from models.oferta import Estado, PerfilRecomendado


# Excepciones personalizadas para errores específicos relacionados con la edición de respuestas de formularios asociados a ofertas de trabajo.
class RespuestaFormularioError(ValueError):
    pass


# Función que obtiene una oferta de trabajo por su ID desde la base de datos
def obtener_oferta_id(id):
    with SessionLocal() as db:
        return oferta_repository.obtener_oferta_id(db, id)


# Función que obtiene una lista de ofertas de trabajo desde la base de datos, con soporte para paginación y filtrado por varios criterios
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


# Funcion que elimina una oferta de trabajo por su ID desde la base de datos
def eliminar_oferta(id):
    with SessionLocal() as db:
        return oferta_repository.eliminar_oferta(db, id)


#Funcion que modifica los datos de una oferta de trabajo por su ID desde la base de datos
def modificar_oferta(id, datos):
    with SessionLocal() as db:
        return oferta_repository.modificar_datos_oferta(db, id, datos)


# Función que marca una oferta de trabajo como error en la base de datos, actualizando su estado a "ERROR"
def marcar_error_oferta(db, id: str):
    return oferta_repository.modificar_datos_oferta(
        db,
        id,
        {
            "estado": Estado.ERROR,
        },
    )

# Funcion para editar la respuesta a una pregunta de un formulario asociado a una oferta de trabajo, validando que la pregunta pertenezca a la oferta y que la respuesta cumpla con los requisitos según el tipo de pregunta
def editar_respuesta_formulario(id: str, pregunta_id: str, datos):
    with SessionLocal() as db:
        # Obtener la oferta de trabajo por su ID desde la base de datos
        oferta = oferta_repository.obtener_oferta_id(db, id)
        if not oferta or oferta.eliminado:
            return None

        # Guardar las preguntas del formulario asociadas a la oferta
        preguntas = oferta.preguntas_formulario or []
        # Validar que la pregunta a editar pertenezca a la oferta
        pregunta = next(
            (item for item in preguntas if item["pregunta_id"] == pregunta_id),
            None,
        )
        if pregunta is None:
            raise RespuestaFormularioError("La pregunta no pertenece a la oferta")

        # Guardar las respuestas del formulario asociadas a la oferta
        respuestas = oferta.respuestas_formulario or []
        # Validar y actualizar la respuesta a la pregunta según el tipo de pregunta y los datos proporcionados
        respuesta_actual = next(
            (item for item in respuestas if item.get("pregunta_id") == pregunta_id),
            {"pregunta_id": pregunta_id},
        ).copy()
        campos = datos.model_fields_set

        # Si la pregunta es de tipo "radio" o "select", se requiere un valor seleccionado válido. Si la pregunta es de tipo "text" o "number", se requiere una respuesta de texto válida
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
                # Validar que el valor seleccionado coincida con una opción válida de la pregunta
                opcion = next(
                    (item for item in pregunta["opciones"] if item["valor"] == valor),
                    None,
                )
                if opcion is None:
                    raise RespuestaFormularioError(
                        "valor_seleccionado no coincide con una opción válida"
                    )
                # Actualizar la respuesta con el texto de la opción seleccionada y marcarla como suficiente
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

            # Validar que la respuesta de texto no esté vacía y actualizar la respuesta con el texto proporcionado, marcándola como suficiente si tiene contenido
            texto = datos.respuesta.strip() if datos.respuesta else None
            respuesta_actual.update(
                respuesta=texto,
                valor_seleccionado=None,
                informacion_suficiente=bool(texto),
            )

        # Actualizar la lista de respuestas del formulario, reemplazando la respuesta existente a la pregunta con la nueva respuesta actualizada
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


# Función que confirma que todas las respuestas obligatorias de un formulario asociado a una oferta de trabajo han sido completadas y válidas, y actualiza el estado de la oferta a "LISTA_PARA_APLICAR" si es así
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

# Función que valida si todas las preguntas obligatorias de un formulario tienen respuestas válidas y suficientes antes de enviar la solicitud
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
