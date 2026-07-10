from scraper.linkedin.scraper import extraer_ofertas
from database import SessionLocal
from repositories import oferta_repository


def ejecutar_scraper_linkedin(busqueda: str):
    try:
        ofertas = extraer_ofertas(busqueda)

        with SessionLocal() as db:
            resultado = oferta_repository.guardar_ofertas(db, ofertas)
            print(resultado, flush=True)
            return {
                "busqueda": busqueda,
                "ofertas_extraidas": len(ofertas),
                **resultado,
            }
    except Exception as e:
        print(f"Error ejecutando scraper: {e}", flush=True)
        raise
