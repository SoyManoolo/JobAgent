from typing import Optional
from database import SessionLocal
from repositories import oferta_repository
from models.oferta import Estado, PerfilRecomendado


def obtener_oferta_id(id):
    with SessionLocal() as db:
        return oferta_repository.obtener_oferta_id(db, id)


def obtener_ofertas(
    pagina: int,
    limite: int,
    estado: Optional[Estado] = None,
    perfil: Optional[PerfilRecomendado] = None,
    score_min: Optional[int] = None,
    empresa: Optional[str] = None,
):
    with SessionLocal() as db:
        return oferta_repository.devolver_ofertas(
            db, pagina, limite, estado, perfil, score_min, empresa
        )


def eliminar_oferta(id):
    with SessionLocal() as db:
        return oferta_repository.eliminar_oferta(db, id)


def modificar_oferta(id, datos):
    with SessionLocal() as db:
        return oferta_repository.modificar_datos_oferta(db, id, datos)
