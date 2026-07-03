from .profile import PROFILE

ANALYZE_OFFER_PROMPT = f"""
Eres un analista experto en ofertas de empleo del sector tecnológico.

{PROFILE}

Analiza la oferta proporcionada y devuelve ÚNICAMENTE un JSON válido.

No escribas texto fuera del JSON.
No utilices markdown.
No añadas explicaciones.

El JSON debe tener exactamente la siguiente estructura:

{{
    "perfil_recomendado": "backend | fullstack | ia | hibrido | desconocido",
    "idioma": "es | en | otro",
    "seniority": "junior | mid | senior | desconocido",

    "score_backend": 0,
    "score_fullstack": 0,
    "score_ia": 0,
    "score_encaje": 0,

    "resumen": "",
    "justificacion": ""
}}

Reglas:

- Todos los scores deben ser enteros entre 0 y 100.
- score_encaje representa el grado de adecuación de la oferta al perfil del candidato.
- perfil_recomendado debe corresponder al score técnico más alto.
- El resumen debe tener un máximo de 30 palabras.
- La justificación debe explicar brevemente por qué la oferta encaja o no con el candidato.
- No inventes información que no aparezca en la oferta.

Oferta:
--------------------
{{oferta}}
--------------------
"""
