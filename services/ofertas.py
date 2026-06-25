from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from models.oferta import Oferta


# Esta es la funcion que devuelve True o False dependiendo de si esa oferta ya existe o no
def existe_oferta(
    db: Session, id_plataforma: str, plataforma: str, titulo: str, empresa: str
):
    mismo_sitio = (
        db.query(Oferta)
        .filter(Oferta.id_plataforma == id_plataforma, Oferta.plataforma == plataforma)
        .first()
    )

    if mismo_sitio is not None:
        return True

    multi_plataforma = (
        db.query(Oferta)
        .filter(
            func.lower(Oferta.empresa) == func.lower(empresa),
            func.lower(Oferta.titulo) == func.lower(titulo),
        )
        .first()
    )

    return multi_plataforma is not None


# Esta es la funcion que se encarga de guardar las nuevas ofertas de trabajo encontradas por el scraper
def guardar_oferta(db: Session, datos: dict):
    nueva_oferta = Oferta(**datos)

    db.add(nueva_oferta)

    db.commit()

    db.refresh(nueva_oferta)

    return nueva_oferta


# Esta es la funcion utilizada para mandarle las ofertas de trabajo que se encuentran pendientes de responder sus preguntas
def devolver_ofertas_pendientes(db: Session, limite: int = 5):
    return (
        db.query(Oferta)
        .filter(Oferta.estado == "PENDIENTE_REVISION")
        .limit(limite)
        .all()
    )


# Funcion para modificar los datos de una oferta, asi como añadir las respuestas a las preguntas
def modificar_datos_oferta(db: Session, id: str, datos: dict):
    oferta = db.get(Oferta, id)

    if not oferta:
        return None

    for clave, valor in datos.items():
        setattr(oferta, clave, valor)

    db.commit()

    db.refresh(oferta)

    return oferta


# Funcion para devolver de manera paginada las ofertas para mostrarlas en la interfaz
def devolver_ofertas_paginadas(db: Session, pagina: int = 1, limite: int = 10):
    salto = (pagina - 1) * limite

    return db.query(Oferta).order_by(desc(Oferta.id)).limit(limite).offset(salto).all()


def eliminar_oferta(db: Session, id: str):
    oferta = db.get(Oferta, id)

    if not oferta:
        return None

    oferta.eliminado = True

    db.commit()

    db.refresh(oferta)

    return oferta
