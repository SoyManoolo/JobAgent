def obtener_texto(locator):
    if locator.count() == 0:
        return None

    return " ".join(locator.first.text_content().split())

