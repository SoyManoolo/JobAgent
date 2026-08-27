# Funcion que obtiene el texto de un elemento web localizado por un localizador, devolviendo None si no se encuentra ningún elemento
def obtener_texto(locator):
    if locator.count() == 0:
        return None

    return " ".join(locator.first.text_content().split())

