from models.oferta import Estado, Oferta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc


def obtener_oferta(db: Session, id: str):
    return db.get(Oferta, id)


# Esta es la funcion que devuelve True o False dependiendo de si esa oferta ya existe o no
def es_oferta_duplicada(
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
def guardar_ofertas(db: Session, ofertas):
    ofertas_guardadas = 0
    ofertas_no_guardadas = 0
    ofertas_duplicadas = 0
    for oferta in ofertas:
        try:
            if es_oferta_duplicada(
                db,
                id_plataforma=oferta["id_plataforma"],
                plataforma=oferta["plataforma"],
                titulo=oferta["titulo"],
                empresa=oferta["empresa"],
            ):
                ofertas_duplicadas += 1
                continue

            nueva_oferta = Oferta(**oferta)

            db.add(nueva_oferta)

            db.commit()

            ofertas_guardadas += 1

        except Exception as e:
            print(e)

            db.rollback()

            ofertas_no_guardadas += 1

    return {
        "ofertas_guardadas": ofertas_guardadas,
        "ofertas_no_guardadas": ofertas_no_guardadas,
        "ofertas_duplicadas": ofertas_duplicadas,
    }


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


def obtener_ofertas_estado(db: Session, estado: Estado):
    return db.query(Oferta).filter(Oferta.estado == estado).all()


# Funcion para devolver de manera paginada las ofertas para mostrarlas en la interfaz
def devolver_ofertas_paginadas(db: Session, pagina: int = 1, limite: int = 10):
    salto = (pagina - 1) * limite

    return (
        db.query(Oferta)
        .filter(Oferta.eliminado == False)
        .order_by(desc(Oferta.id))
        .limit(limite)
        .offset(salto)
        .all()
    )


def eliminar_oferta(db: Session, id: str):
    oferta = db.get(Oferta, id)

    if not oferta:
        return None

    oferta.eliminado = True

    db.commit()

    db.refresh(oferta)

    return oferta


def obtener_stats(db: Session):
    query_base = db.query(Oferta).filter(Oferta.eliminado == False)

    total = query_base.count()

    pendientes = query_base.filter(Oferta.estado == Estado.PENDIENTE_REVISION).count()
    aplicadas = query_base.filter(Oferta.estado == Estado.APLICADA).count()
    descartadas = query_base.filter(Oferta.estado == Estado.DESCARTADA).count()
    return {
        "total_ofertas": total,
        "aplicadas": aplicadas,
        "pendientes": pendientes,
        "descartadas": descartadas,
    }


def modificar_notas(db: Session, id: str, nota: str):
    oferta = db.get(Oferta, id)

    if not oferta:
        return None

    oferta.notas = nota

    db.commit()

    db.refresh(oferta)

    return oferta