import requests
import json
import dotenv

URL_OLLAMA = ""


def analizar_oferta(descripcion: str) -> dict:
    payload = {
        "model": "",
        "messages": [
            {
                "role": "system",
                "content": "Debes de analizar esta oferta y decidir si encaja con mi perfil, no tengo porque encajar al 100%, pero si por lo menos un 75%. Además de que debes elegir que tipo de perfil encaja más con el trabajo: BACKEND, FULLSTACK o IA",
            },
            {"role": "system", "content": f"Oferta:\n{descripcion}"},
        ],
        "format": "json",
        "stream": False,
    }

    response = requests.post(URL_OLLAMA, json=payload)
    response.raise_for_status()
    return json.loads(response.json()["message"]["content"])


def responder_preguntas(preguntas: str) -> dict:
    payload = {
        "model": "",
        "messages": [
            {
                "role": "system",
                "content": "Debes de responder las preguntas basándote en la información de mi curriculum y mis datos",
            },
            {"role": "system", "content": f"Preguntas:\n{preguntas}"},
        ],
        "format": "json",
        "stream": False,
    }

    response = requests.post(URL_OLLAMA, json=payload)
    response.raise_for_status()
    return json.loads(response.json()["message"]["content"])
