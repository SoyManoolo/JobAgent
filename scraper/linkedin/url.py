import re
from urllib.parse import urlsplit


_RUTA_OFERTA = re.compile(r"/jobs/view/[0-9]+/?\Z")
_HOSTS_LINKEDIN = {"linkedin.com", "www.linkedin.com"}


def validar_url_oferta_linkedin(url: str) -> str:
    """Acepta únicamente enlaces HTTPS a una oferta concreta de LinkedIn."""
    if not isinstance(url, str) or any(ord(char) <= 32 or ord(char) == 127 for char in url):
        raise ValueError("La URL debe ser una oferta HTTPS de LinkedIn")

    try:
        partes = urlsplit(url)
        valida = (
            partes.scheme == "https"
            and partes.hostname in _HOSTS_LINKEDIN
            and partes.port is None
            and partes.username is None
            and partes.password is None
            and _RUTA_OFERTA.fullmatch(partes.path) is not None
            and not partes.fragment
        )
    except ValueError:
        valida = False

    if not valida:
        raise ValueError("La URL debe ser una oferta HTTPS de LinkedIn")
    return url
