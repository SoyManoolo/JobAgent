import requests
import json
import os
from dotenv import load_dotenv
from agent.prompts import answer_question
from agent.prompts.analyze_offer import ANALYZE_OFFER_PROMPT
from agent.prompts.answer_question import ANSWER_QUESTION_PROMPT

load_dotenv()

URL_OLLAMA = os.getenv("OLLAMA_URL") or "localhost:11434/v1/"
MODEL = os.getenv("OLLAMA_MODEL")


def analizar_oferta(descripcion: str) -> dict:
    prompt = ANALYZE_OFFER_PROMPT.format(oferta=descripcion)

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

    response = requests.post(URL_OLLAMA, json=payload)
    response.raise_for_status()

    contenido = response.json()["message"]["content"]

    return json.loads(contenido)


def responder_preguntas(preguntas: str) -> dict:
    prompt = ANSWER_QUESTION_PROMPT.format(pregunta=preguntas)
    payload = {
        "model": "",
        "messages": [
            {
                "role": "system",
                "content": prompt,
            }
        ],
        "format": "json",
        "stream": False,
    }

    response = requests.post(URL_OLLAMA, json=payload)
    response.raise_for_status()

    contenido = response.json()["message"]["content"]

    return json.loads(contenido)
