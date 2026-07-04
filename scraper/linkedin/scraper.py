from scraper.browser import crear_navegador

playwright, browser, context, page = crear_navegador(persistent=True)

page.goto("https://www.linkedin.com/feed/")

input("pulsa Enter para cerrar...")

context.close()
playwright.stop()
