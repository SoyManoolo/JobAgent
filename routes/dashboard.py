from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from repositories import oferta_repository

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats")
def obtener_estadisticas(db: Session = Depends(get_db)):
    return oferta_repository.obtener_stats(db)


@router.patch("/ofertas/{id}/notas")
def actualizar_notas(
    id: str, notas: str = Body(embed=True), db: Session = Depends(get_db)
):
    oferta = oferta_repository.modificar_notas(db, id, notas)
    if oferta is None:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta
