from fastapi import FastAPI, HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from services import ofertas as ofertas_service

router = APIRouter(prefix="/ofertas", tags=["Ofertas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", status_code=status.HTTP_200_OK)
def obtener_ofertas(pagina: int = 1, limite: int = 10, db: Session = Depends(get_db)):
    return ofertas_service.devolver_ofertas_paginadas(db, pagina, limite)


@router.post("/{id}/aplicar", status_code=status.HTTP_200_OK)
def aplicar_oferta(id: str, db: Session = Depends(get_db)):
    # Aqui tengo que llamar a la funcion que se encarga de llamar al modelo de ollama para que haga la aplicacion a la oferta de trabajo
    return {}


@router.patch("/{id}", status_code=status.HTTP_200_OK)
def modificar_respuestas(id: str, preguntas: dict, db: Session = Depends(get_db)):
    oferta_actualizada = ofertas_service.modificar_datos_oferta(db, id, preguntas)

    if not oferta_actualizada:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    return oferta_actualizada


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_oferta(
    id: str,
    db: Session = Depends(get_db),
):
    oferta_eliminada = ofertas_service.eliminar_oferta(db, id)

    if not oferta_eliminada:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"status": "deleted", "id": id}
