from typing import Optional
from models.oferta import Estado, Oferta, PerfilRecomendado
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uuid


# Función para obtener una oferta por su ID
def obtener_oferta_id(db: Session, id: str):
    return db.get(Oferta, id)


# Esta es la funcion que devuelve True o False dependiendo de si esa oferta ya existe o no
def es_oferta_duplicada(
    db: Session, id_plataforma: str, plataforma: str, titulo: str, empresa: str
):
    # Primero, verifica si hay una oferta con el mismo id_plataforma y plataforma
    mismo_sitio = (
        db.query(Oferta)
        .filter(Oferta.id_plataforma == id_plataforma, Oferta.plataforma == plataforma)
        .first()
    )

    if mismo_sitio is not None:
        return True

    # Luego, verifica si hay una oferta con el mismo titulo y empresa, ignorando mayúsculas y minúsculas
    multi_plataforma = (
        db.query(Oferta)
        .filter(
            func.lower(Oferta.empresa) == func.lower(empresa),
            func.lower(Oferta.titulo) == func.lower(titulo),
        )
        .first()
    )

    # Si encontramos una oferta con el mismo titulo y empresa, pero en otra plataforma, consideramos que es duplicada
    return multi_plataforma is not None


# Esta es la funcion que se encarga de guardar las nuevas ofertas de trabajo encontradas por el scraper
def guardar_ofertas(db: Session, ofertas):
    # Contadores para estadísticas
    ofertas_guardadas = 0
    ofertas_no_guardadas = 0
    ofertas_duplicadas = 0

    # Itera sobre cada oferta y la guarda en la base de datos si no es duplicada
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

            # Agrega la nueva oferta a la sesión de la base de datos
            db.add(nueva_oferta)

            # Commit de la transacción para guardar la oferta en la base de datos
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
    # Obtiene la oferta de la base de datos por su ID
    oferta = db.get(Oferta, id)

    if not oferta:
        return None

    # Modifica los atributos de la oferta con los datos proporcionados
    for clave, valor in datos.items():
        setattr(oferta, clave, valor)

    # Commit de la transacción para guardar los cambios en la base de datos
    db.commit()

    # Refresca la instancia de la oferta para reflejar los cambios en la base de datos
    db.refresh(oferta)

    return oferta

# Función para obtener ofertas por estado, con un límite opcional
def obtener_ofertas_estado(db: Session, estado: Estado, limite: Optional[int] = 10):
    query = db.query(Oferta).filter(
        Oferta.estado == estado,
        Oferta.eliminado.is_(False),
    )
    if limite:
        query = query.limit(limite)
    return query.all()


# Función para obtener ofertas por perfil recomendado, con un límite opcional
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
    # Calcula el desplazamiento para la paginación
    salto = (pagina - 1) * limite

    # Construye la consulta base para obtener ofertas de trabajo
    query = db.query(Oferta)

    # Aplica filtros según los parámetros proporcionados
    query = query.filter(Oferta.eliminado == False)

    # Aplica filtros según los parámetros proporcionados
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

    # Obtiene el total de ofertas que cumplen con los filtros aplicados
    total = query.count()

    # Obtiene las ofertas de trabajo ordenadas por ID en orden descendente, aplicando la paginación
    ofertas = query.order_by(desc(Oferta.id)).offset(salto).limit(limite).all()

    return ofertas, total


# Función para obtener ofertas que necesitan extraer preguntas de formulario, con un límite opcional
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


# Función para eliminar una oferta de trabajo por su ID
def eliminar_oferta(db: Session, id: str):
    oferta = db.get(Oferta, id)

    if not oferta:
        return None

    oferta.eliminado = True

    db.commit()

    db.refresh(oferta)

    return oferta


# Función para modificar las notas de una oferta de trabajo por su ID
def modificar_notas(db: Session, id: str, notas: str):
    return modificar_datos_oferta(db, id, {"notas": notas})
