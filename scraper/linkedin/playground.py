from scraper.browser import crear_navegador

def main():
    playwright, _, context, page = crear_navegador(persistent=True, headless=False)
    try:
        page.goto("https://www.linkedin.com/jobs/", wait_until="domcontentloaded")
        input("Inicia sesión en LinkedIn y pulsa ENTER para guardar el perfil y cerrar...")
    finally:
        try:
            context.close()
        finally:
            playwright.stop()


if __name__ == "__main__":
    main()
