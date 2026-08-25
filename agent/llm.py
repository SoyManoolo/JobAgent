import requests
import json
import os
from dotenv import load_dotenv
from agent.prompts.analyze_offer import build_analyze_prompt
from agent.prompts.answer_question import build_answer_questions_prompt
from services.retry import ejecutar_con_reintentos

load_dotenv()
# URL de Ollama
URL_OLLAMA = os.getenv("OLLAMA_URL") or "http://localhost:11434/api/chat"
# Modelo de Ollama a utilizar
MODEL = os.getenv("OLLAMA_MODEL")
# Tiempo máximo de espera para la respuesta de Ollama (en segundos)
REQUEST_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "60"))
# Numero máximo de tokens generados por Ollama en la respuesta
NUM_PREDICT = max(1, int(os.getenv("OLLAMA_NUM_PREDICT", "350")))
# Temperatura de la generación de texto por Ollama (0.0 a 1.0)
TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))
# Número máximo de tokens de contexto que Ollama puede utilizar (en tokens)
NUM_CTX = max(1, int(os.getenv("OLLAMA_NUM_CTX", "16384")))
# Indica si se debe utilizar la opción "think" de Ollama (True o False)
THINK = os.getenv("OLLAMA_THINK", "false").lower() in {"1", "true", "yes"}
# Indica el tiempo que Ollama debe mantener la conexión abierta después de la última solicitud
KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "10m")

# Definición de los valores válidos para los campos de perfil, idioma y seniority
PERFILES = {"backend", "ia", "desconocido"}
IDIOMAS = {"es", "en", "ca", "otro"}
SENIORITY = {"junior", "mid", "senior", "desconocido"}


# Función para obtener las opciones de configuración de Ollama
def _opciones_ollama() -> dict:
    return {
        "num_predict": NUM_PREDICT,
        "temperature": TEMPERATURE,
        "num_ctx": NUM_CTX,
    }


# Función para analizar una oferta de trabajo utilizando Ollama con reintentos en caso de error
def analizar_oferta(descripcion: str) -> dict:
    return ejecutar_con_reintentos(
        lambda: _analizar_oferta(descripcion),
        "el análisis de la oferta con Ollama",
    )


# Función interna para analizar una oferta de trabajo utilizando Ollama
def _analizar_oferta(descripcion: str) -> dict:
    # Construye el prompt para analizar la oferta
    prompt = build_analyze_prompt(descripcion)

    # Construye el payload para la solicitud a Ollama
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "format": "json",
        "stream": False,
        "think": THINK,
        "keep_alive": KEEP_ALIVE,
        "options": _opciones_ollama(),
    }

    # Realiza la solicitud POST a Ollama y guarda la respuesta
    response = requests.post(URL_OLLAMA, json=payload, timeout=REQUEST_TIMEOUT)
    # Verifica si la respuesta fue exitosa, si no, lanza una excepción
    response.raise_for_status()

    # Obtiene el contenido de la respuesta y lo convierte a un diccionario
    raw = response.json()

    contenido = raw["message"]["content"]
    resultado = json.loads(contenido)

    # Normaliza los valores de los campos a minúsculas y valida que estén dentro de los valores permitidos
    resultado["perfil_recomendado"] = resultado["perfil_recomendado"].lower()
    resultado["idioma"] = resultado["idioma"].lower()
    resultado["seniority"] = resultado["seniority"].lower()

    # Validación de los campos del resultado para asegurar que tengan valores válidos
    if resultado["perfil_recomendado"] not in PERFILES:
        resultado["perfil_recomendado"] = "desconocido"

    if resultado["idioma"] not in IDIOMAS:
        resultado["idioma"] = "otro"

    if resultado["seniority"] not in SENIORITY:
        resultado["seniority"] = "desconocido"

    # Validación de que todos los campos requeridos estén presentes en el resultado
    campos = [
        "perfil_recomendado",
        "idioma",
        "seniority",
        "score_backend",
        "score_ia",
        "score_encaje",
        "resumen",
        "motivo_encaje",
    ]

    for campo in campos:
        if campo not in resultado:
            raise ValueError(f"Falta el campo '{campo}'")

    return resultado


# Función para responder preguntas sobre una oferta de trabajo utilizando Ollama con reintentos en caso de error
def responder_preguntas_oferta(oferta: str, cv: str, preguntas: list[dict]) -> dict:
    return ejecutar_con_reintentos(
        lambda: _responder_preguntas_oferta(oferta, cv, preguntas),
        "la generación de respuestas con Ollama",
    )


# Función interna para responder preguntas sobre una oferta de trabajo utilizando Ollama
def _responder_preguntas_oferta(
    oferta: str, cv: str, preguntas: list[dict]
) -> dict:
    # Construye el prompt para responder preguntas sobre la oferta
    prompt = build_answer_questions_prompt(oferta, cv, preguntas)

    # Construye el payload para la solicitud a Ollama
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": prompt,
            }
        ],
        "format": "json",
        "stream": False,
        "think": THINK,
        "keep_alive": KEEP_ALIVE,
        "options": _opciones_ollama(),
    }

    # Realiza la solicitud POST a Ollama y guarda la respuesta
    response = requests.post(URL_OLLAMA, json=payload, timeout=REQUEST_TIMEOUT)
    # Verifica si la respuesta fue exitosa, si no, lanza una excepción
    response.raise_for_status()

    raw = response.json()
    contenido = raw["message"]["content"]

    # Muestra la respuesta bruta de Ollama y el contenido procesado para depuración
    print(
        "Respuesta bruta de Ollama al generar respuestas: "
        + json.dumps(raw, ensure_ascii=False, default=str),
        flush=True,
    )
    print(
        f"Contenido de Ollama al generar respuestas: {contenido}",
        flush=True,
    )

    return json.loads(contenido)
