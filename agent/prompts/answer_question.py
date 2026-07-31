import json

from .technologies import TECHNOLOGIES
from .application_preferences import APPLICATION_PREFERENCES


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
- Usa "Preferencias de candidatura" para preguntas de disponibilidad, ubicación, modalidad, salario, autorización laboral, formación, idiomas y condiciones de trabajo.
- Para preguntas de tipo `number` sobre años de experiencia con una tecnología que no aparezca en el contexto, responde `0` y marca `informacion_suficiente: true`.
- Para cualquier otro caso en que falte información suficiente, responde de forma honesta y profesional.
- Responde estrictamente en el mismo idioma que cada pregunta, aunque el CV esté en otro idioma.
- Las respuestas deben ser naturales, directas y concisas.
- No deduzcas que el candidato posee un título, experiencia o disponibilidad si no aparece de forma explícita en el contexto.
- No equipares un CFGS, un título de Técnico Superior o un curso de especialización con un Bachelor's Degree o grado universitario.
- Para preguntas de tipo `radio` o `select`, elige una opción solo si el contexto permite justificarla.
- Para preguntas de tipo `radio` o `select` con información suficiente, copia exactamente el campo `valor` de la opción elegida en `valor_seleccionado`.
- Para preguntas de tipo `text` o `number`, `valor_seleccionado` debe ser `null`.
- `informacion_suficiente` indica si la respuesta propuesta está respaldada por el contexto; no indica si la respuesta es positiva, negativa, cero o desfavorable.
- Si no hay información suficiente, usa siempre `respuesta: null`, `valor_seleccionado: null` e `informacion_suficiente: false`. No propongas "No", "0", texto condicional ni ninguna otra respuesta en ese caso.
- Si incluyes cualquier valor en `respuesta` o `valor_seleccionado`, `informacion_suficiente` debe ser siempre `true`.
- El valor `0` en una pregunta numérica es una respuesta válida y debe llevar `informacion_suficiente: true`; nunca marques como insuficiente una respuesta numérica con valor `0`.
- Una pregunta de selección no admite explicaciones ni respuestas condicionales: elige exactamente una de sus opciones con `informacion_suficiente: true`, o devuelve ambos valores como `null` con `informacion_suficiente: false`.
- No menciones las fuentes de contexto utilizadas.
- Responde a todas las preguntas recibidas en exactamente el mismo orden en que aparecen en `Preguntas`.
- No incluyas `pregunta_id`: el sistema asociará cada respuesta con su pregunta según la posición.
- Devuelve únicamente JSON válido.
- No utilices Markdown ni escribas texto fuera del JSON.

El JSON debe tener exactamente esta estructura:

{{
    "respuestas": [
        {{
            "respuesta": "respuesta generada o null",
            "valor_seleccionado": "valor exacto de la opción elegida o null",
            "informacion_suficiente": true
        }}
    ]
}}

Ejemplos obligatorios de coherencia:

Pregunta `number` sin experiencia conocida en la tecnología:
```json
{{"respuesta": "0", "valor_seleccionado": null, "informacion_suficiente": true}}
```

Pregunta `select` cuya respuesta no se puede justificar con el contexto:
```json
{{"respuesta": null, "valor_seleccionado": null, "informacion_suficiente": false}}
```

Pregunta `radio` con una respuesta justificada y opción `No`:
```json
{{"respuesta": "No", "valor_seleccionado": "No", "informacion_suficiente": true}}
```

Nunca devuelvas estas combinaciones inválidas:

```json
{{"respuesta": "No", "valor_seleccionado": "No", "informacion_suficiente": false}}
{{"respuesta": "0", "valor_seleccionado": null, "informacion_suficiente": false}}
{{"respuesta": "Sí, pero prefiero remoto", "valor_seleccionado": null, "informacion_suficiente": false}}
```

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

Preferencias de candidatura:
--------------------
{APPLICATION_PREFERENCES}
--------------------

Preguntas:
--------------------
{preguntas_json}
--------------------
"""
