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

# Nombre exacto del documento ya subido a LinkedIn para cada CV. Este fichero
# es una plantilla: configura los nombres reales en tu copia privada cv.py.
CVS_LINKEDIN = {
    "backend_es": "CV_ES_BACKEND.pdf",
    "backend_en": "CV_EN_BACKEND.pdf",
    "ia_es": "CV_ES_IA.pdf",
    "ia_en": "CV_EN_IA.pdf",
}


def obtener_cv(perfil: str, idioma: str) -> str:
    """Devuelve el CV adecuado para el perfil e idioma solicitados."""
    idioma_cv = "en" if idioma == "en" else "es"
    clave = f"{perfil}_{idioma_cv}"

    if clave not in CVS:
        raise ValueError(f"No hay CV disponible para el perfil '{perfil}'")

    return CVS[clave]


def obtener_nombre_cv_linkedin(perfil: str, idioma: str) -> str:
    """Devuelve el nombre del documento que se debe elegir en LinkedIn."""
    idioma_cv = "en" if idioma == "en" else "es"
    clave = f"{perfil}_{idioma_cv}"

    if clave not in CVS_LINKEDIN:
        raise ValueError(
            f"No hay un documento de LinkedIn configurado para el CV '{clave}'"
        )

    return CVS_LINKEDIN[clave]
