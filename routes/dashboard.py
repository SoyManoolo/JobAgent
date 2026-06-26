from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from services import dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats")
def obtener_estadisticas(db: Session = Depends(get_db)):
    return dashboard.obtener_stats(db)


@router.patch("/ofertas/{id}/notas")
def actualizar_notas(
    id: str, notas: str = Body(embed=True), db: Session = Depends(get_db)
):
    return dashboard.modificar_notas(db, id, notas)
