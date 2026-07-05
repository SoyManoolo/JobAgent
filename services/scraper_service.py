from database import SessionLocal
from repositories.oferta_repository import guardar_ofertas
from scraper.linkedin.scraper import extraer_ofertas


def ejecutar_scraper_linkedin():
    ofertas = extraer_ofertas()

    with SessionLocal() as db:
        resultado = guardar_ofertas(db, ofertas)

    return resultado

