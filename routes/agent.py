from fastapi import APIRouter, HTTPException, status
from services import agent_service

router = APIRouter(prefix="/agent", tags=["Agente"])


@router.post("/ofertas/procesar")
def procesar_ofertas():
    return agent_service.procesar_ofertas_extraidas()


@router.post("/ofertas/procesar/{id}")
def procesar_oferta(id: str):
    oferta = agent_service.procesar_oferta(id)
    if not oferta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta no encontrada")

    return oferta


@router.post("/ofertas/responder")
def responder_preguntas_ofertas():
    return agent_service.responder_preguntas_ofertas()


@router.post("/ofertas/responder/{id}")
def responder_preguntas_oferta(id: str):
    return agent_service.responder_preguntas_oferta(id)
