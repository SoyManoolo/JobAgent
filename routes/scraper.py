from fastapi import APIRouter, HTTPException, status
from services import scraper_service

router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/linkedin", status_code=status.HTTP_200_OK)
def extraer_ofertas_linkedin(busqueda: str = "Backend"):
    return scraper_service.ejecutar_scraper_linkedin(busqueda)


@router.post("/linkedin/easyapply/procesar")
def extraer_preguntas_pendientes(limite: int = 10):
    return scraper_service.ejecutar_scraper_preguntas_pendientes(limite)


@router.post("/linkedin/easyapply/procesar/{id}", status_code=status.HTTP_200_OK)
def extraer_preguntas_oferta(id: str):
    return scraper_service.ejecutar_scraper_preguntas_linkedin(id)


@router.post("/linkedin/easyapply/aplicar/{id}", status_code=status.HTTP_200_OK)
def aplicar_oferta(id: str):
    try:
        return scraper_service.ejecutar_aplicacion_easy_apply(id)
    except scraper_service.OfertaNoEncontradaError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except scraper_service.OfertaNoListaParaAplicarError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except scraper_service.CvLinkedInNoConfiguradoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/infojobs", status_code=status.HTTP_200_OK)
def extraer_ofertas_infojobs():
    return ""


@router.post("/indeed", status_code=status.HTTP_200_OK)
def extraer_ofertas_indeed():
    return ""


@router.post("/glassdoor", status_code=status.HTTP_200_OK)
def extraer_ofertas_glassdoor():
    return ""
