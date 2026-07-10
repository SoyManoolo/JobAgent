from fastapi import APIRouter
from services import agent_service

router = APIRouter(prefix="/agent", tags=["Agente"])


@router.post("/ofertas/procesar")
def procesar_ofertas():
    print("Ha llegado la peticion")
    return agent_service.procesar_ofertas_extraidas()
