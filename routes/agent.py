from fastapi import APIRouter
from services import agent_service

router = APIRouter(prefix="/agent", tags=["Agente"])


@router.post("/ofertas/procesar")
def procesar_ofertas():
    print("Ha llegado la peticion")
    return agent_service.procesar_ofertas_extraidas()


@router.post("/ofertas/responder")
def responder_preguntas_ofertas():
    return agent_service.responder_preguntas_ofertas()


@router.post("/ofertas/{id}/responder")
def responder_preguntas_oferta(id: str):
    return agent_service.responder_preguntas_oferta(id)