from scraper.browser import crear_navegador
from scraper.utils import obtener_texto
import re

BUSQUEDAS = [
    "Backend",
    "Backend Developer",
    "Python",
    "Java",
    "Fullstack",
    "Full Stack",
    "Machine Learning",
    "Artificial Intelligence",
    "AI Engineer",
]

MAX_OFERTAS = 200


def extraer_ofertas():
    """
    Extrae ofertas de LinkedIn para todas las búsquedas definidas
    en BUSQUEDAS y devuelve una lista de diccionarios.
    """

    ofertas_extraidas = []
    ids_vistos = set()

    playwright, _, context, page = crear_navegador(persistent=True)
    try:
        for busqueda in BUSQUEDAS:
            url = f"https://www.linkedin.com/jobs/search/?keywords={busqueda}"

            response = page.goto(url, wait_until="domcontentloaded")

            if response:
                print(response.status)

            ultimo_total = 0

            while True:
                ofertas = page.locator(".job-card-container")
                total = ofertas.count()

                if total >= MAX_OFERTAS or total == ultimo_total:
                    break

                ultimo_total = total

                for _ in range(5):
                    page.evaluate("""
                        () => {
                            const lista = document
                                .querySelector("[data-results-list-top-scroll-sentinel]")
                                .parentElement;
                            lista.scrollTop += 600;
                        }
                    """)
                    page.wait_for_timeout(300)

            ofertas = page.locator(".job-card-container")

            print(f"\nTotal de ofertas: {ofertas.count()}")

            for i in range(ofertas.count()):
                try:
                    oferta = ofertas.nth(i)

                    titulo = oferta.locator("a.job-card-list__title--link")
                    titulo_texto = obtener_texto(titulo)

                    link = titulo.get_attribute("href")

                    if not link:
                        continue

                    if link.startswith("/"):
                        link = f"https://www.linkedin.com{link}"

                    raw_id_plataforma = re.search(r"/jobs/view/(\d+)", link)

                    if not raw_id_plataforma:
                        continue

                    id_plataforma = raw_id_plataforma.group(1)

                    if id_plataforma in ids_vistos:
                        continue

                    ids_vistos.add(id_plataforma)

                    empresa = obtener_texto(
                        oferta.locator(".artdeco-entity-lockup__subtitle")
                    )

                    metadatos = oferta.locator(".job-card-container__metadata-wrapper")

                    ubicacion = obtener_texto(metadatos.first)

                    salario = None

                    if metadatos.count() > 1:
                        salario = obtener_texto(metadatos.nth(1))

                    titulo.click()

                    page.wait_for_selector(".jobs-description-content__text--stretch")

                    datos_publicacion = obtener_texto(
                        page.locator(
                            ".job-details-jobs-unified-top-card__tertiary-description-container"
                        )
                    )

                    coincidencia = re.search(r"hace\s+[^·]+", datos_publicacion)

                    fecha_publicacion = (
                        coincidencia.group().strip() if coincidencia else None
                    )

                    descripcion = obtener_texto(
                        page.locator(".jobs-description-content__text--stretch")
                    )

                    oferta_data = {
                        "id_plataforma": id_plataforma,
                        "plataforma": "linkedin",
                        "titulo": titulo_texto,
                        "empresa": empresa,
                        "ubicacion": ubicacion,
                        "salario": salario,
                        "url": link,
                        "descripcion": descripcion,
                        "fecha_publicacion": fecha_publicacion,
                    }

                    ofertas_extraidas.append(oferta_data)
                except Exception as e:
                    print(e)
                    continue

            page.wait_for_timeout(1000)

        return ofertas_extraidas

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    ofertas = extraer_ofertas()
    print(len(ofertas))
