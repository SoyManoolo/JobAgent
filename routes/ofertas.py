from typing import Optional
from fastapi import APIRouter, HTTPException, status
from models.oferta import Estado, PerfilRecomendado
from schemas.oferta_schema import RespuestaFormularioUpdate
from services import oferta_service

router = APIRouter(prefix="/ofertas", tags=["Ofertas"])


@router.get("/", status_code=status.HTTP_200_OK)
def obtener_ofertas(
    pagina: int = 1,
    limite: int = 10,
    estado: Optional[Estado] = None,
    perfil: Optional[PerfilRecomendado] = None,
    score_min: Optional[int] = None,
    empresa: Optional[str] = None,
    aplicacion_sencilla: Optional[bool] = None,
):
    return oferta_service.obtener_ofertas(
        pagina, limite, estado, perfil, score_min, empresa, aplicacion_sencilla
    )


@router.get("/{id}")
def obtener_oferta(id: str):
    oferta = oferta_service.obtener_oferta_id(id)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    return oferta


@router.patch("/{id}/respuestas/{pregunta_id}")
def editar_respuesta_formulario(
    id: str,
    pregunta_id: str,
    datos: RespuestaFormularioUpdate,
):
    try:
        resultado = oferta_service.editar_respuesta_formulario(id, pregunta_id, datos)
    except oferta_service.RespuestaFormularioError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    if resultado is None:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return resultado


@router.post("/{id}/respuestas/confirmar")
def confirmar_respuestas_formulario(id: str):
    try:
        oferta = oferta_service.confirmar_respuestas_formulario(id)
    except oferta_service.RespuestaFormularioError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if oferta is None:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta


@router.patch("/{id}", status_code=status.HTTP_200_OK)
def modificar_datos_oferta(id: str, datos: dict):
    oferta = oferta_service.modificar_oferta(id, datos)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    return oferta


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_oferta(id: str):
    oferta = oferta_service.eliminar_oferta(id)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    return oferta
