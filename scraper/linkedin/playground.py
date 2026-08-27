from scraper.browser import crear_navegador

# Codigo de prueba para verificar la funcionalidad del navegador y la interacción con la página web, navegando de manera manual

playwright, browser, context, page = crear_navegador(persistent=True)

url = "https://www.linkedin.com/jobs/"

page.goto(url, wait_until="domcontentloaded")

input("Inspecciona la página y pulsa ENTER para cerrar...")

context.close()
playwright.stop()
