from fastapi import APIRouter, HTTPException, Query, status
from services import agent_service

router = APIRouter(prefix="/agent", tags=["Agente"])


def _error_ollama_en_uso(error: agent_service.OllamaEnUsoError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@router.post("/ofertas/procesar")
def procesar_ofertas(limite: int = Query(default=25, ge=1, le=100)):
    try:
        return agent_service.procesar_ofertas_extraidas(limite=limite)
    except agent_service.OllamaEnUsoError as error:
        raise _error_ollama_en_uso(error) from error
    except agent_service.AnalisisEnCursoError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.post("/ofertas/procesar/{id}")
def procesar_oferta(id: str):
    try:
        oferta = agent_service.procesar_oferta(id)
    except agent_service.OllamaEnUsoError as error:
        raise _error_ollama_en_uso(error) from error
    except agent_service.AnalisisEnCursoError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    if not oferta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oferta no encontrada")

    return oferta


@router.post("/ofertas/responder")
def responder_preguntas_ofertas(limite: int = Query(default=5, ge=1, le=100)):
    try:
        return agent_service.responder_preguntas_ofertas(limite=limite)
    except agent_service.OllamaEnUsoError as error:
        raise _error_ollama_en_uso(error) from error


@router.post("/ofertas/responder/{id}")
def responder_preguntas_oferta(id: str):
    try:
        resultado = agent_service.responder_preguntas_oferta(id)
    except agent_service.OllamaEnUsoError as error:
        raise _error_ollama_en_uso(error) from error
    except agent_service.RespuestaFormularioError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except agent_service.OllamaNoDisponibleError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except agent_service.RespuestaOllamaInvalidaError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oferta no encontrada",
        )
    return resultado
