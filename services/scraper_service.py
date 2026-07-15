from operator import le
from scraper.linkedin.jobs_scraper import extraer_ofertas
from scraper.linkedin.easy_apply_scraper import extraer_preguntas
from database import SessionLocal
from repositories import oferta_repository


def ejecutar_scraper_linkedin(busqueda: str):
    try:
        ofertas = extraer_ofertas(busqueda)

        with SessionLocal() as db:
            resultado = oferta_repository.guardar_ofertas(db, ofertas)
            return {
                "busqueda": busqueda,
                "ofertas_extraidas": len(ofertas),
                **resultado,
            }
    except Exception as e:
        print(f"Error ejecutando scraper: {e}", flush=True)
        raise


def ejecutar_scraper_preguntas_linkedin(id: str):
    with SessionLocal() as db:
        oferta = oferta_repository.obtener_oferta_id(db, id)

        if oferta is None:
            raise ValueError("Oferta no encontrada")

        if not oferta.aplicacion_sencilla:
            raise ValueError("La oferta no tiene solicitud sencilla")

        preguntas = extraer_preguntas(oferta.url)

        resultado = oferta_repository.modificar_datos_oferta(
            db, id, {"preguntas_formulario": preguntas}
        )

        return {
            "oferta_id": id,
            "total_preguntas": len(preguntas),
            "preguntas": preguntas,
            "resultado": resultado,
        }
