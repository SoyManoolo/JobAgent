import random
import re
from urllib.parse import urlencode

from playwright.sync_api import Error as PlaywrightError

from scraper.browser import crear_navegador
from scraper.utils import obtener_texto


MAX_OFERTAS = 200


def extraer_ofertas(busqueda: str) -> list[dict]:
    ofertas_extraidas = []
    ids_vistos = set()

    playwright, _, context, page = crear_navegador(persistent=True)

    try:
        parametros = urlencode({"keywords": busqueda})
        url = f"https://www.linkedin.com/jobs/search/?{parametros}"

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60_000,
            )
        except PlaywrightError as error:
            raise RuntimeError(
                f"LinkedIn rechazó la búsqueda '{busqueda}': {error}"
            ) from error

        page.locator(".job-card-container").first.wait_for(
            state="visible",
            timeout=60_000,
        )

        ultimo_total = 0

        while True:
            ofertas = page.locator(".job-card-container")
            total = ofertas.count()

            if total >= MAX_OFERTAS or total == ultimo_total:
                break

            ultimo_total = total

            for _ in range(5):
                desplazado = page.evaluate(
                    """
                    () => {
                        const sentinel = document.querySelector(
                            "[data-results-list-top-scroll-sentinel]"
                        );

                        if (!sentinel || !sentinel.parentElement) {
                            return false;
                        }

                        sentinel.parentElement.scrollTop += 600;
                        return true;
                    }
                    """
                )

                if not desplazado:
                    break

                page.wait_for_timeout(random.randint(250, 600))

        ofertas = page.locator(".job-card-container")
        total = min(ofertas.count(), MAX_OFERTAS)

        print(
            f"Total de ofertas para '{busqueda}': {total}",
            flush=True,
        )

        for i in range(total):
            try:
                oferta = ofertas.nth(i)

                titulo = oferta.locator("a.job-card-list__title--link").first

                titulo_texto = obtener_texto(titulo)
                link = titulo.get_attribute("href")

                if not link:
                    continue

                if link.startswith("/"):
                    link = f"https://www.linkedin.com{link}"

                coincidencia_id = re.search(
                    r"/jobs/view/(\d+)",
                    link,
                )

                if not coincidencia_id:
                    continue

                id_plataforma = coincidencia_id.group(1)

                if id_plataforma in ids_vistos:
                    continue

                empresa = obtener_texto(
                    oferta.locator(".artdeco-entity-lockup__subtitle").first
                )

                metadatos = oferta.locator(".job-card-container__metadata-wrapper")

                ubicacion = obtener_texto(metadatos.first)

                salario = None

                if metadatos.count() > 1:
                    salario = obtener_texto(metadatos.nth(1))

                titulo.click()

                descripcion_locator = page.locator(
                    ".jobs-description-content__text--stretch"
                ).first

                descripcion_locator.wait_for(
                    state="visible",
                    timeout=60_000,
                )

                descripcion = obtener_texto(descripcion_locator)

                ofertas_extraidas.append(
                    {
                        "id_plataforma": id_plataforma,
                        "plataforma": "linkedin",
                        "titulo": titulo_texto,
                        "empresa": empresa,
                        "ubicacion": ubicacion,
                        "salario": salario,
                        "url": link,
                        "descripcion": descripcion,
                    }
                )

                ids_vistos.add(id_plataforma)

                page.wait_for_timeout(random.randint(500, 1200))

            except Exception as error:
                print(
                    f"Error procesando oferta {i + 1}: {error}",
                    flush=True,
                )
                continue

        return ofertas_extraidas

    finally:
        context.close()
        playwright.stop()

