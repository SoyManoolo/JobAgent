from typing import Optional
from models.oferta import Estado, Oferta, PerfilRecomendado
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid


def obtener_oferta_id(db: Session, id: str):
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

            datos = oferta.copy()

            datos["id"] = str(uuid.uuid4())
            datos["estado"] = Estado.EXTRAIDA

            nueva_oferta = Oferta(**datos)

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


def obtener_ofertas_estado(db: Session, estado: Estado, limite: Optional[int] = 10):
    query = db.query(Oferta).filter(
        Oferta.estado == estado,
        Oferta.eliminado.is_(False),
    )
    if limite:
        query = query.limit(limite)
    return query.all()


def devolver_ofertas(
    db: Session,
    pagina: int = 1,
    limite: int = 10,
    estado: Optional[Estado] = None,
    perfil: Optional[PerfilRecomendado] = None,
    score_min: Optional[int] = None,
    empresa: Optional[str] = None,
    aplicacion_sencilla: Optional[bool] = None,
):
    salto = (pagina - 1) * limite

    query = db.query(Oferta)

    query = query.filter(Oferta.eliminado == False)

    if estado is not None:
        query = query.filter(Oferta.estado == estado)

    if perfil is not None:
        query = query.filter(Oferta.perfil_recomendado == perfil)

    if score_min is not None:
        query = query.filter(Oferta.score_encaje >= score_min)

    if empresa:
        query = query.filter(Oferta.empresa.ilike(f"%{empresa}%"))

    if aplicacion_sencilla is not None:
        query = query.filter(Oferta.aplicacion_sencilla == aplicacion_sencilla)

    total = query.count()

    ofertas = query.order_by(desc(Oferta.id)).offset(salto).limit(limite).all()

    return ofertas, total


def obtener_ofertas_para_extraer_preguntas(
    db: Session,
    limite: int = 10,
):
    return (
        db.query(Oferta)
        .filter(
            Oferta.estado == Estado.ANALIZADA,
            Oferta.aplicacion_sencilla.is_(True),
            Oferta.preguntas_formulario.is_(None),
            Oferta.eliminado.is_(False),
        )
        .limit(limite)
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


def modificar_notas(db: Session, id: str, notas: str):
    return modificar_datos_oferta(db, id, {"notas": notas})


def obtener_stats(db: Session):
    query_base = db.query(Oferta).filter(Oferta.eliminado == False)

    total = query_base.count()

    aplicadas = query_base.filter(Oferta.estado == Estado.APLICADA).count()
    descartadas = query_base.filter(Oferta.estado == Estado.DESCARTADA).count()
    return {
        "total_ofertas": total,
        "aplicadas": aplicadas,
        "descartadas": descartadas,
    }
