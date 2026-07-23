from fastapi import APIRouter, status
from services import scraper_service

router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/linkedin", status_code=status.HTTP_200_OK)
def extraer_ofertas_linkedin(busqueda: str = "Backend"):
    return scraper_service.ejecutar_scraper_linkedin(busqueda)


@router.post("/linkedin/easyapply/procesar")
def extraer_preguntas_pendientes(limite: int = 10):
    return scraper_service.ejecutar_scraper_preguntas_pendientes(
        limite
    )

@router.post("/linkedin/easyapply/procesar/{id}", status_code=status.HTTP_200_OK)
def extraer_preguntas_oferta(id: str):
    return scraper_service.ejecutar_scraper_preguntas_linkedin(id)


@router.post("/infojobs", status_code=status.HTTP_200_OK)
def extraer_ofertas_infojobs():
    return ""


@router.post("/indeed", status_code=status.HTTP_200_OK)
def extraer_ofertas_indeed():
    return ""


@router.post("/glassdoor", status_code=status.HTTP_200_OK)
def extraer_ofertas_glassdoor():
    return ""
