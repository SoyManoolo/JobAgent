from playwright.sync_api import Error as PlaywrightError

from scraper.browser import crear_navegador


class SolicitudNoDisponibleError(Exception):
    pass


def extraer_preguntas(link: str) -> list[dict]:
    playwright, _, context, page = crear_navegador(
        persistent=True,
    )

    try:
        try:
            page.goto(
                link,
                wait_until="domcontentloaded",
                timeout=60_000,
            )
        except PlaywrightError as error:
            raise RuntimeError(
                f"LinkedIn rechazó la navegación a '{link}': {error}"
            ) from error

        easy_apply = page.locator(
            'a[aria-label="Solicitud sencilla"], a[href*="openSDUIApplyFlow=true"]'
        ).first

        try:
            easy_apply.wait_for(
                state="visible",
                timeout=5_000,
            )
        except TimeoutError as error:
            raise SolicitudNoDisponibleError(
                "La oferta ya no admite Solicitud Sencilla"
            ) from error

        easy_apply.click()

        # Paso 1: datos de contacto
        next_button = page.locator("button[data-easy-apply-next-button]").first

        next_button.wait_for(
            state="visible",
            timeout=60_000,
        )
        next_button.click()

        # Paso 2: selección de currículum
        next_button.wait_for(
            state="visible",
            timeout=60_000,
        )
        next_button.click()

        # Paso 3: preguntas adicionales
        page.wait_for_timeout(1_000)

        preguntas = extraer_preguntas_paso(page)

        print(
            f"Preguntas detectadas: {len(preguntas)}",
            flush=True,
        )

        return preguntas

    finally:
        context.close()
        playwright.stop()


def extraer_preguntas_paso(page) -> list[dict]:
    preguntas = []

    elementos = page.locator("[data-test-form-element]")

    print(
        f"Elementos detectados en el paso: {elementos.count()}",
        flush=True,
    )

    for i in range(elementos.count()):
        elemento = elementos.nth(i)

        componente_texto = elemento.locator(
            "[data-test-single-line-text-form-component]"
        )

        if componente_texto.count() > 0:
            label = componente_texto.locator("label").first
            input_element = componente_texto.locator("input").first

            texto = label.inner_text().strip()
            input_id = input_element.get_attribute("id") or ""

            tipo = (
                "number"
                if input_id.endswith("-numeric")
                or "años de experiencia" in texto.lower()
                or "expectativa salarial" in texto.lower()
                else "text"
            )

            pregunta = {
                "pregunta_id": input_id or f"pregunta_{i}",
                "texto": texto,
                "tipo": tipo,
                "obligatoria": (input_element.get_attribute("required") is not None),
                "selector_temporal": (f"#{input_id}" if input_id else None),
                "opciones": [],
            }

            print("Pregunta texto:", pregunta, flush=True)
            preguntas.append(pregunta)
            continue

        componente_radio = elemento.locator(
            '[data-test-form-builder-radio-button-form-component="true"]'
        )

        if componente_radio.count() > 0:
            titulo = componente_radio.locator(
                "[data-test-form-builder-radio-button-form-component__title]"
            ).first

            opciones_locator = componente_radio.locator('input[type="radio"]')

            opciones = []

            for j in range(opciones_locator.count()):
                opcion = opciones_locator.nth(j)

                opciones.append(
                    {
                        "texto": opcion.get_attribute(
                            "data-test-text-selectable-option__input"
                        ),
                        "valor": opcion.get_attribute("value"),
                    }
                )

            pregunta = {
                "pregunta_id": (
                    componente_radio.get_attribute("id") or f"pregunta_{i}"
                ),
                "texto": titulo.inner_text().strip(),
                "tipo": "radio",
                "obligatoria": (
                    componente_radio.locator(
                        "[data-test-form-builder-radio-button-form-component__required]"
                    ).count()
                    > 0
                ),
                "selector_temporal": (
                    f"#{componente_radio.get_attribute('id')}"
                    if componente_radio.get_attribute("id")
                    else None
                ),
                "opciones": opciones,
            }

            print("Pregunta radio:", pregunta, flush=True)
            preguntas.append(pregunta)
            continue

        componente_select = elemento.locator(
            "[data-test-text-entity-list-form-component]"
        )

        if componente_select.count() > 0:
            label = componente_select.locator("label").first
            select_element = componente_select.locator("select").first

            opciones = []

            option_elements = select_element.locator("option")

            for j in range(option_elements.count()):
                option = option_elements.nth(j)

                texto = option.inner_text().strip()
                valor = option.get_attribute("value")

                if texto.lower() == "selecciona una opción":
                    continue

                opciones.append(
                    {
                        "texto": texto,
                        "valor": valor,
                    }
                )

            select_id = select_element.get_attribute("id")

            pregunta = {
                "pregunta_id": select_id or f"pregunta_{i}",
                "texto": label.inner_text().strip(),
                "tipo": "select",
                "obligatoria": (select_element.get_attribute("required") is not None),
                "selector_temporal": (f"#{select_id}" if select_id else None),
                "opciones": opciones,
            }

            print("Pregunta select:", pregunta, flush=True)
            preguntas.append(pregunta)

    return preguntas
