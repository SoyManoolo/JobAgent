from browser import crear_navegador

playwright, browser, context, page = crear_navegador()

page.goto(
    "https://www.linkedin.com/jobs/search-results/?currentJobId=4389789491&eBP=NON_CHARGEABLE_CHANNEL&refId=ml54VZyDxsqsg03msOJaFw%3D%3D&trackingId=ylgK2JScnvD%2Ff3a1aW%2FB3w%3D%3D&showHowYouFit=HOW_YOU_FIT&keywords=Desarrollador%20backend%20junior&origin=QUALIFICATION_LANDING&geoId=100256124"
)

print(page.title())

print(page.url)

buscador = page.locator('textarea[name="q"]')

print(buscador.count())

buscador.fill("playwright python")

buscador.press("Enter")

primer_resultado = page.locator("h3").first
print(primer_resultado.text_content())

input("Pulsa ENTER para cerrar...")

browser.close()
playwright.stop()
