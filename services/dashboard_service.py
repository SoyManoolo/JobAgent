from database import SessionLocal
from repositories import dashboard_repository, oferta_repository


def obtener_stats():
    with SessionLocal() as db:
        return dashboard_repository.obtener_stats(db)


def modificar_notas(id: str, notas: str):
    with SessionLocal() as db:
        return oferta_repository.modificar_notas(db, id, notas)
