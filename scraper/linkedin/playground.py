from scraper.browser import crear_navegador

playwright, browser, context, page = crear_navegador(persistent=True)

url = "https://www.linkedin.com/jobs/"

page.goto(url, wait_until="domcontentloaded")

input("Inspecciona la página y pulsa ENTER para cerrar...")

context.close()
playwright.stop()
