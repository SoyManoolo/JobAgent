import json

from .technologies import TECHNOLOGIES


def build_answer_questions_prompt(
    oferta: str,
    cv: str,
    preguntas: list[dict],
) -> str:
    technologies_json = json.dumps(
        TECHNOLOGIES,
        ensure_ascii=False,
        indent=2,
    )

    preguntas_json = json.dumps(
        preguntas,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Eres un asistente especializado en responder preguntas de formularios de procesos de selección.

Utiliza únicamente la información proporcionada en la oferta, el CV y la experiencia tecnológica del candidato.

Reglas:

- No inventes experiencias, tecnologías, fechas, responsabilidades ni años de experiencia.
- Diferencia entre experiencia profesional, académica y en proyectos personales.
- No presentes experiencia académica o personal como experiencia profesional.
- Para preguntas sobre tecnologías o tiempo de experiencia, prioriza la información de "Experiencia tecnológica".
- Si falta información suficiente, responde de forma honesta y profesional.
- Adapta cada respuesta al idioma de la pregunta.
- Las respuestas deben ser naturales, directas y concisas.
- No menciones las fuentes de contexto utilizadas.
- Conserva exactamente el identificador de cada pregunta.
- Responde a todas las preguntas recibidas.
- Devuelve únicamente JSON válido.
- No utilices Markdown ni escribas texto fuera del JSON.

El JSON debe tener exactamente esta estructura:

{{
    "respuestas": [
        {{
            "pregunta_id": "identificador original",
            "respuesta": "respuesta generada",
            "informacion_suficiente": true
        }}
    ]
}}

Oferta:
--------------------
{oferta}
--------------------

CV:
--------------------
{cv}
--------------------

Experiencia tecnológica:
--------------------
{technologies_json}
--------------------

Preguntas:
--------------------
{preguntas_json}
--------------------
"""