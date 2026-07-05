from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from repositories import oferta_repository

router = APIRouter(prefix="/ofertas", tags=["Ofertas"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", status_code=status.HTTP_200_OK)
def obtener_ofertas(pagina: int = 1, limite: int = 10, db: Session = Depends(get_db)):
    return oferta_repository.devolver_ofertas_paginadas(db, pagina, limite)


@router.get("/{id}")
def obtener_oferta(id: str, db: Session = Depends(get_db)):
    oferta = oferta_repository.obtener_oferta(db, id)
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta


@router.post("/{id}/aplicar", status_code=status.HTTP_200_OK)
def aplicar_oferta(id: str, db: Session = Depends(get_db)):
    # Aqui tengo que llamar a la funcion que se encarga de llamar al modelo de ollama para que haga la aplicacion a la oferta de trabajo
    return {}


@router.patch("/{id}", status_code=status.HTTP_200_OK)
def modificar_respuestas(id: str, preguntas: dict, db: Session = Depends(get_db)):
    oferta_actualizada = oferta_repository.modificar_datos_oferta(db, id, preguntas)

    if not oferta_actualizada:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    return oferta_actualizada


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_oferta(
    id: str,
    db: Session = Depends(get_db),
):
    oferta_eliminada = oferta_repository.eliminar_oferta(db, id)

    if not oferta_eliminada:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return {"status": "deleted", "id": id}
