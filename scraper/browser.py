from playwright.sync_api import sync_playwright


# Funcion que crea un navegador web con Playwright
def crear_navegador(persistent=False, *, headless=True):
    # Inicializar Playwright y lanzar un navegador Chromium
    playwright = sync_playwright().start()

    # Si se solicita un contexto persistente, se lanza un navegador con un perfil de usuario guardado en el directorio "profile", lo que permite mantener la sesión y las cookies entre ejecuciones
    if persistent:
        browser = None
        context = playwright.chromium.launch_persistent_context(
            user_data_dir="profile",
            headless=headless,
        )

        # Se reutiliza la primera página del contexto si ya existe, o se crea una nueva página si no hay ninguna abierta
        page = context.new_page() if len(context.pages) == 0 else context.pages[0]

        return playwright, browser, context, page

    browser = playwright.chromium.launch(headless=headless)

    context = browser.new_context()

    page = context.new_page()

    return playwright, browser, context, page
