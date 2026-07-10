from fastapi import APIRouter, status
from services import scraper_service

router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/linkedin", status_code=status.HTTP_200_OK)
def extraer_ofertas_linkedin(busqueda: str = "Backend"):
    return scraper_service.ejecutar_scraper_linkedin(busqueda)


@router.post("/infojobs", status_code=status.HTTP_200_OK)
def extraer_ofertas_infojobs():
    return ""


@router.post("/indeed", status_code=status.HTTP_200_OK)
def extraer_ofertas_indeed():
    return ""


@router.post("/glassdoor", status_code=status.HTTP_200_OK)
def extraer_ofertas_glassdoor():
    return ""
