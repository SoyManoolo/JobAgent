from fastapi import APIRouter, Body, HTTPException
from services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def obtener_estadisticas():
    return dashboard_service.obtener_stats()


@router.patch("/ofertas/{id}/notas")
def actualizar_notas(id: str, notas: str = Body(embed=True)):
    oferta = dashboard_service.modificar_notas(id, notas)
    if oferta is None:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta
