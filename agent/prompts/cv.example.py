"""Plantilla local de CV para JobAgent.

Copia este archivo como ``cv.py`` y reemplaza los textos de ejemplo. El archivo
``cv.py`` está ignorado por Git para evitar publicar datos personales.
"""

CVS = {
    "backend_es": """BACKEND DEVELOPER\n\n[Añade aquí tu CV en español]""",
    "backend_en": """BACKEND DEVELOPER\n\n[Add your English CV here]""",
    "ia_es": """INGENIERO/A DE IA\n\n[Añade aquí tu CV en español]""",
    "ia_en": """AI ENGINEER\n\n[Add your English CV here]""",
}


def obtener_cv(perfil: str, idioma: str) -> str:
    """Devuelve el CV adecuado para el perfil e idioma solicitados."""
    idioma_cv = "en" if idioma == "en" else "es"
    clave = f"{perfil}_{idioma_cv}"

    if clave not in CVS:
        raise ValueError(f"No hay CV disponible para el perfil '{perfil}'")

    return CVS[clave]
