from .profile import PROFILE


def build_analyze_prompt(oferta: str) -> str:
    return f"""
Eres un analista experto en ofertas de empleo tecnológicas.

{PROFILE}

Analiza la oferta y devuelve ÚNICAMENTE un JSON válido.
No escribas texto fuera del JSON.
No utilices markdown.
No añadas explicaciones.

El JSON debe tener exactamente esta estructura:

{{
    "perfil_recomendado": "backend | ia | desconocido",
    "idioma": "es | en | otro",
    "seniority": "junior | mid | senior | desconocido",
    "score_backend": 0,
    "score_ia": 0,
    "score_encaje": 0,
    "resumen": "",
    "motivo_encaje": ""
}}

Criterios de perfil:
- backend: APIs, servicios, bases de datos, backend, Python, FastAPI, Java, Spring Boot, Node.js, Express, NestJS.
- ia: IA aplicada, LLMs, automatización inteligente, ML, data science, NLP, RAG, agentes, Python para IA.
- desconocido: oferta no tecnológica, genérica, sysadmin puro, soporte IT puro, candidatura espontánea o sin rol claro.

Reglas de scoring:
- score_backend y score_ia miden afinidad técnica con cada perfil.
- score_encaje mide si merece la pena que el candidato revise/aplique a la oferta.
- No bases score_encaje solo en tecnologías coincidentes.
- Penaliza fuerte si el seniority requerido es superior al perfil junior del candidato.
- Penaliza fuerte si exige muchos años de experiencia profesional.
- Penaliza fuerte si el rol no es de desarrollo de software.
- Penaliza si el stack principal está lejos del perfil: PHP puro, Ruby puro, SAP, soporte, sistemas, redes, helpdesk.
- Penaliza si requiere C1/C2 de inglés o inglés profesional avanzado.
- Penaliza si la oferta es senior, lead, architect, staff o principal.
- Penaliza si la oferta no describe un puesto concreto.

Rangos para score_encaje:
- 0-19: no encaja; debe descartarse.
- 20-39: encaje bajo; solo revisar si no hay mejores opciones.
- 40-59: encaje medio; revisable pero con dudas claras.
- 60-79: buen encaje; merece revisión.
- 80-100: encaje muy alto; prioridad.

Reglas concretas:
- Si la oferta no es tecnológica, score_encaje debe ser 0-10 y perfil_recomendado "desconocido".
- Si es sysadmin, soporte IT, técnico de sistemas o redes sin desarrollo real, score_encaje máximo 20.
- Si es candidatura espontánea o oferta genérica sin rol técnico concreto, score_encaje máximo 20.
- Si pide senior, lead, architect, staff o principal, score_encaje máximo 55 aunque el stack coincida.
- Si pide 4 o más años de experiencia, score_encaje máximo 60.
- Si pide 2-3 años de experiencia, score_encaje máximo 75.
- Si pide 0-1 años, prácticas, trainee, junior o formación, no penalices por experiencia.
- Si pide tecnologías del stack principal del candidato y es junior/mid bajo, puede superar 80.
- Si combina desarrollo backend con IA aplicada o automatización real, puede superar 85.
- perfil_recomendado debe corresponder al score técnico más alto.
- Si backend e IA tienen scores similares y ambos son relevantes, elige el perfil que mejor represente la función principal del puesto.
- Todos los scores deben ser enteros entre 0 y 100.
- resumen máximo 30 palabras.
- motivo_encaje debe explicar brevemente los principales puntos a favor y en contra.
- No inventes información que no aparezca en la oferta.

Oferta:
--------------------
{oferta}
--------------------
"""
