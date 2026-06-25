from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas.oferta_schema import OfertaCreate
from services import ofertas
from agent import llm

router = APIRouter(prefix="/agent", tags=["Agente"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ofertas/procesar")
def ofertas_pend(db: Session = Depends(get_db)):
    lista_ofertas = ofertas.devolver_ofertas_pendientes(db)

    for oferta in lista_ofertas:
        try:
            resultado = llm.analizar_oferta()

            datos_actualizar = {
                "preguntas_formulario": resultado,
                "estado": "PROCESADA",
            }
            ofertas.modificar_datos_oferta(db, oferta.id, datos_actualizar)
        except Exception as e:
            print(f"Error procesando la oferta {oferta.id}: {e}")
        continue

    return {"procesadas": len(lista_ofertas)}


@router.post("/ofertas")
def subir_oferta(datos: OfertaCreate, db: Session = Depends(get_db)):
    duplicada = ofertas.existe_oferta(
        db,
        id_plataforma=datos.id_plataforma,
        plataforma=datos.plataforma,
        titulo=datos.titulo,
        empresa=datos.empresa,
    )

    if duplicada:
        raise HTTPException(status_code=400, detail="Esta oferta ya ha sido procesada")

    nueva_oferta = ofertas.guardar_oferta(db, datos=datos.model_dump())

    return {"id": nueva_oferta.id}


@router.patch("/ofertas/{id}/analizar")
def modificar_oferta(id: str, datos: dict, db: Session = Depends(get_db)):
    oferta_actualizada = ofertas.modificar_datos_oferta(db, id, datos)

    if not oferta_actualizada:
        raise HTTPException(status_code=404, detail="Esta oferta no existe")

    return {"id": id}
