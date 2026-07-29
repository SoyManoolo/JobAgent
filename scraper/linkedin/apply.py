import re
import unicodedata

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from scraper.browser import crear_navegador
from scraper.linkedin.easy_apply_scraper import abrir_easy_apply


MAX_PASOS_FORMULARIO = 12


class FormularioEasyApplyError(Exception):
    """El formulario no coincide con las preguntas y respuestas guardadas."""


class EnvioNoConfirmadoError(Exception):
    """LinkedIn no confirmó el envío después de pulsar el botón final."""


def enviar_solicitud(
    link: str,
    preguntas: list[dict],
    respuestas: list[dict],
    nombre_cv: str,
) -> dict:
    """Rellena y envía una solicitud Easy Apply previamente revisada."""
    playwright, _, context, page = crear_navegador(persistent=True)

    try:
        try:
            page.goto(link, wait_until="domcontentloaded", timeout=60_000)
        except PlaywrightError as error:
            raise RuntimeError(
                f"LinkedIn rechazó la navegación a '{link}': {error}"
            ) from error

        if _solicitud_ya_enviada(page):
            return {
                "enviada": True,
                "ya_enviada": True,
                "campos_rellenados": 0,
            }

        abrir_easy_apply(page)

        respuestas_por_id = {
            respuesta["pregunta_id"]: respuesta for respuesta in respuestas
        }
        preguntas_por_texto = {
            _normalizar_texto(pregunta["texto"]): pregunta["pregunta_id"]
            for pregunta in preguntas
        }
        preguntas_utilizadas = set()
        campos_rellenados = 0
        cv_seleccionado = False

        for _ in range(MAX_PASOS_FORMULARIO):
            page.wait_for_timeout(500)
            if not cv_seleccionado:
                cv_seleccionado = _seleccionar_cv_linkedin(page, nombre_cv)
            campos_rellenados += _rellenar_preguntas_visibles(
                page,
                preguntas,
                respuestas_por_id,
                preguntas_por_texto,
                preguntas_utilizadas,
            )

            accion, boton = _esperar_siguiente_accion(page)

            if accion == "enviar":
                _validar_preguntas_obligatorias(
                    preguntas,
                    respuestas_por_id,
                    preguntas_utilizadas,
                )
                boton.click()
                _esperar_confirmacion_envio(page)
                return {
                    "enviada": True,
                    "ya_enviada": False,
                    "campos_rellenados": campos_rellenados,
                    "cv_seleccionado": nombre_cv,
                }

            if accion == "revisar":
                boton.click()
                continue

            if accion == "siguiente":
                boton.click()
                # Algunas pantallas de Easy Apply terminan de renderizar sus
                # preguntas cuando se intenta avanzar. Si LinkedIn bloquea el
                # avance por un obligatorio, se escanean de nuevo esos campos
                # antes de considerarlo un error definitivo.
                page.wait_for_timeout(750)
                error_validacion = _obtener_error_validacion(page)
                if error_validacion is not None:
                    rellenadas_despues_de_validacion = _rellenar_preguntas_visibles(
                        page,
                        preguntas,
                        respuestas_por_id,
                        preguntas_por_texto,
                        preguntas_utilizadas,
                    )
                    campos_rellenados += rellenadas_despues_de_validacion
                    if rellenadas_despues_de_validacion > 0:
                        continue
                    raise FormularioEasyApplyError(error_validacion)
                continue

        raise FormularioEasyApplyError(
            f"El formulario superó el máximo de {MAX_PASOS_FORMULARIO} pasos"
        )
    finally:
        context.close()
        playwright.stop()


def _seleccionar_cv_linkedin(page, nombre_cv: str) -> bool:
    """Selecciona el documento de LinkedIn cuyo nombre se configuró localmente."""
    _desplegar_todos_los_cvs(page)
    documentos = page.locator('input[id^="jobsDocumentCardToggle-"]')
    if documentos.count() == 0:
        return False

    nombre_normalizado = _normalizar_texto(nombre_cv)
    disponibles = []

    for indice in range(documentos.count()):
        documento = documentos.nth(indice)
        etiqueta = documento.evaluate(
            "element => element.labels?.[0]?.innerText?.trim() || ''"
        )
        disponibles.append(etiqueta)
        if nombre_normalizado not in _normalizar_texto(etiqueta):
            continue

        if not documento.is_checked():
            identificador = documento.get_attribute("id")
            etiqueta_documento = page.locator(
                f'label[for="{identificador}"]'
            ).first
            if etiqueta_documento.count() > 0:
                # El botón de descarga puede cubrir visualmente el input. El
                # label está asociado al mismo radio y evita ese solapamiento.
                etiqueta_documento.click(force=True)
            else:
                documento.check(force=True)

        if not documento.is_checked():
            raise FormularioEasyApplyError(
                f"LinkedIn no confirmó la selección del CV '{nombre_cv}'"
            )

        return True

    raise FormularioEasyApplyError(
        f"No se encontró el CV configurado '{nombre_cv}'. "
        f"Documentos visibles: {disponibles}"
    )


def _desplegar_todos_los_cvs(page) -> None:
    """Expande las tarjetas de CV que LinkedIn oculta tras «Mostrar más»."""
    for _ in range(5):
        botones = page.locator(
            "button.jobs-document-upload__show-more-less-button:visible"
        )
        boton_mostrar = None

        for indice in range(botones.count()):
            boton = botones.nth(indice)
            texto = _normalizar_texto(boton.inner_text())
            if "mostrar" in texto or "show more" in texto:
                boton_mostrar = boton
                break

        if boton_mostrar is None:
            return

        documentos_antes = page.locator(
            'input[id^="jobsDocumentCardToggle-"]'
        ).count()
        boton_mostrar.click()
        try:
            page.wait_for_function(
                """cantidadAnterior =>
                document.querySelectorAll(
                    'input[id^="jobsDocumentCardToggle-"]'
                ).length > cantidadAnterior""",
                arg=documentos_antes,
                timeout=3_000,
            )
        except PlaywrightTimeoutError:
            # LinkedIn puede tardar en actualizar el texto del botón aunque
            # no haya más documentos que desplegar.
            page.wait_for_timeout(300)


def _esperar_siguiente_accion(page):
    """Espera a que LinkedIn muestre la siguiente acción del formulario."""
    botones = {
        "enviar": page.locator(
            "button[data-easy-apply-submit-button], "
            "button:has-text('Enviar solicitud'), "
            "button:has-text('Submit application')"
        ).first,
        "revisar": page.locator(
            "button[data-easy-apply-review-button], "
            "button:has-text('Revisar'), "
            "button:has-text('Review')"
        ).first,
        "siguiente": page.locator("button[data-easy-apply-next-button]").first,
    }

    for _ in range(20):
        for nombre, boton in botones.items():
            if boton.is_visible():
                return nombre, boton
        page.wait_for_timeout(250)

    raise FormularioEasyApplyError(
        "No se encontró un botón para continuar, revisar o enviar"
    )


def _rellenar_preguntas_visibles(
    page,
    preguntas: list[dict],
    respuestas_por_id: dict[str, dict],
    preguntas_por_texto: dict[str, str],
    preguntas_utilizadas: set[str],
) -> int:
    rellenadas = 0
    elementos = page.locator("[data-test-form-element]")

    for indice in range(elementos.count()):
        elemento = elementos.nth(indice)

        componente_texto = elemento.locator(
            "[data-test-single-line-text-form-component]"
        )
        if componente_texto.count() > 0:
            etiqueta = componente_texto.locator("label").first.inner_text().strip()
            campo = componente_texto.locator("input").first
            identificador = campo.get_attribute("id")
            pregunta_id = _buscar_pregunta_id(
                identificador,
                etiqueta,
                respuestas_por_id,
                preguntas_por_texto,
            )
            if pregunta_id is None:
                continue

            respuesta = respuestas_por_id[pregunta_id]
            valor = respuesta.get("respuesta")
            if valor is not None:
                campo.fill(str(valor))
                preguntas_utilizadas.add(pregunta_id)
                rellenadas += 1
            continue

        componente_radio = elemento.locator(
            '[data-test-form-builder-radio-button-form-component="true"]'
        )
        if componente_radio.count() > 0:
            etiqueta = componente_radio.locator(
                "[data-test-form-builder-radio-button-form-component__title]"
            ).first.inner_text().strip()
            pregunta_id = _buscar_pregunta_id(
                componente_radio.get_attribute("id"),
                etiqueta,
                respuestas_por_id,
                preguntas_por_texto,
            )
            if pregunta_id is None:
                continue

            valor = respuestas_por_id[pregunta_id].get("valor_seleccionado")
            if valor is not None:
                _seleccionar_radio(componente_radio, str(valor))
                preguntas_utilizadas.add(pregunta_id)
                rellenadas += 1
            continue

        componente_select = elemento.locator(
            "[data-test-text-entity-list-form-component]"
        )
        if componente_select.count() > 0:
            etiqueta = componente_select.locator("label").first.inner_text().strip()
            campo = componente_select.locator("select").first
            identificador = campo.get_attribute("id")
            pregunta_id = _buscar_pregunta_id(
                identificador,
                etiqueta,
                respuestas_por_id,
                preguntas_por_texto,
            )
            if pregunta_id is None:
                continue

            valor = respuestas_por_id[pregunta_id].get("valor_seleccionado")
            if valor is not None:
                campo.select_option(value=str(valor))
                preguntas_utilizadas.add(pregunta_id)
                rellenadas += 1

    return rellenadas + _rellenar_por_etiqueta(
        page,
        preguntas,
        respuestas_por_id,
        preguntas_utilizadas,
    )


def _rellenar_por_etiqueta(
    page,
    preguntas: list[dict],
    respuestas_por_id: dict[str, dict],
    preguntas_utilizadas: set[str],
) -> int:
    """Alternativa para campos que LinkedIn renderiza fuera del contenedor esperado."""
    rellenadas = 0

    for pregunta in preguntas:
        pregunta_id = pregunta["pregunta_id"]
        if pregunta_id in preguntas_utilizadas or pregunta["tipo"] == "radio":
            continue

        respuesta = respuestas_por_id.get(pregunta_id)
        if respuesta is None:
            continue

        campo = page.get_by_label(pregunta["texto"], exact=False).first
        if not campo.is_visible():
            continue

        if pregunta["tipo"] in {"text", "number"}:
            valor = respuesta.get("respuesta")
            if valor is None:
                continue
            campo.fill(str(valor))
        elif pregunta["tipo"] == "select":
            valor = respuesta.get("valor_seleccionado")
            if valor is None:
                continue
            campo.select_option(value=str(valor))
        else:
            continue

        preguntas_utilizadas.add(pregunta_id)
        rellenadas += 1
    return rellenadas


def _buscar_pregunta_id(
    identificador: str | None,
    texto: str,
    respuestas_por_id: dict[str, dict],
    preguntas_por_texto: dict[str, str],
) -> str | None:
    if identificador and identificador in respuestas_por_id:
        return identificador
    return preguntas_por_texto.get(_normalizar_texto(texto))


def _seleccionar_radio(componente, valor: str) -> None:
    opciones = componente.locator('input[type="radio"]')
    for indice in range(opciones.count()):
        opcion = opciones.nth(indice)
        if opcion.get_attribute("value") == valor:
            opcion.check()
            return
    raise FormularioEasyApplyError(
        f"No se encontró la opción de radio con valor '{valor}'"
    )


def _validar_preguntas_obligatorias(
    preguntas: list[dict],
    respuestas_por_id: dict[str, dict],
    preguntas_utilizadas: set[str],
) -> None:
    pendientes = []

    for pregunta in preguntas:
        if not pregunta.get("obligatoria"):
            continue

        pregunta_id = pregunta["pregunta_id"]
        respuesta = respuestas_por_id.get(pregunta_id)
        if (
            respuesta is None
            or not respuesta.get("informacion_suficiente")
            or pregunta_id not in preguntas_utilizadas
        ):
            pendientes.append(pregunta.get("texto", pregunta_id))

    if pendientes:
        raise FormularioEasyApplyError(
            "No se pudieron completar las preguntas obligatorias: "
            + ", ".join(pendientes)
        )


def _obtener_error_validacion(page) -> str | None:
    alertas = page.locator(
        "[role='alert']:visible, "
        ".artdeco-inline-feedback--error:visible"
    )
    if alertas.count() > 0:
        texto = alertas.first.inner_text().strip()
        return f"LinkedIn rechazó un campo del formulario: {texto or 'valor no válido'}"

    campos_invalidos = page.locator(
        "input:invalid:visible, select:invalid:visible, textarea:invalid:visible"
    )
    if campos_invalidos.count() == 0:
        return None

    campo = campos_invalidos.first
    detalle = campo.evaluate(
        """element => ({
            id: element.id,
            name: element.name,
            etiqueta: element.labels?.[0]?.innerText?.trim(),
            mensaje: element.validationMessage
        })"""
    )
    identificador = detalle["etiqueta"] or detalle["name"] or detalle["id"]
    mensaje = detalle["mensaje"] or "valor no válido"
    return f"LinkedIn rechazó el campo '{identificador}': {mensaje}"


def _esperar_confirmacion_envio(page) -> None:
    confirmacion = page.get_by_text(
        re.compile(
            r"solicitud enviada|solicitud se ha enviado|"
            r"application (?:was )?sent",
            re.IGNORECASE,
        )
    ).first
    try:
        confirmacion.wait_for(state="visible", timeout=15_000)
    except PlaywrightTimeoutError as error:
        raise EnvioNoConfirmadoError(
            "Se pulsó Enviar, pero LinkedIn no confirmó la solicitud"
        ) from error


def _solicitud_ya_enviada(page) -> bool:
    indicador = page.get_by_text(
        re.compile(r"solicitud enviada|application submitted|applied", re.IGNORECASE)
    ).first
    return indicador.is_visible()


def _normalizar_texto(texto: str) -> str:
    texto_sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )
    return " ".join(re.sub(r"[^a-z0-9]+", " ", texto_sin_acentos.casefold()).split())
