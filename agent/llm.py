import requests
import json
import os
from dotenv import load_dotenv
from agent.prompts.analyze_offer import build_analyze_prompt
from agent.prompts.answer_question import build_answer_questions_prompt

load_dotenv()

URL_OLLAMA = os.getenv("OLLAMA_URL") or "http://localhost:11434/api/chat"
MODEL = os.getenv("OLLAMA_MODEL")
REQUEST_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "60"))

PERFILES = {"backend", "ia", "desconocido"}
IDIOMAS = {"es", "en", "ca", "otro"}
SENIORITY = {"junior", "mid", "senior", "desconocido"}


def analizar_oferta(descripcion: str) -> dict:
    try:
        prompt = build_analyze_prompt(descripcion)

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
        }
        print("Enviando peticion a Ollama...")
        response = requests.post(URL_OLLAMA, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        raw = response.json()

        contenido = raw["message"]["content"]
        print("Contenido: ", contenido)

        resultado = json.loads(contenido)

        resultado["perfil_recomendado"] = resultado["perfil_recomendado"].lower()
        resultado["idioma"] = resultado["idioma"].lower()
        resultado["seniority"] = resultado["seniority"].lower()

        if resultado["perfil_recomendado"] not in PERFILES:
            resultado["perfil_recomendado"] = "desconocido"

        if resultado["idioma"] not in IDIOMAS:
            resultado["idioma"] = "otro"

        if resultado["seniority"] not in SENIORITY:
            resultado["seniority"] = "desconocido"

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
    except Exception as e:
        print(e)
        raise


def responder_preguntas_oferta(oferta: str, cv: str, preguntas: list[dict]) -> dict:
    prompt = build_answer_questions_prompt(oferta, cv, preguntas)
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
    }

    response = requests.post(URL_OLLAMA, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    contenido = response.json()["message"]["content"]

    return json.loads(contenido)
