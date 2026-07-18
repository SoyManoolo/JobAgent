"""
Contexto estructurado sobre experiencia tecnológica para JobAgent.

Los campos `inicio_aproximado` y `experiencia_aproximada` deben completarse
solo con datos que el candidato pueda defender en una entrevista.
No deben inferirse automáticamente a partir de la duración de los estudios.
"""

TECHNOLOGIES = {
    "Python": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Desarrollo de APIs con FastAPI",
            "Automatización de procesos",
            "Integración de LLMs locales",
            "Machine Learning y Deep Learning",
            "Scripts de procesamiento de datos",
        ],
        "proyectos": ["JobAgent", "LookR"],
    },
    "TypeScript": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Desarrollo backend con Express.js",
            "Desarrollo frontend con React y Remix",
            "APIs REST",
            "Comunicación en tiempo real",
        ],
        "proyectos": ["Lleure Time", "FriendsGo"],
    },
    "JavaScript": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Desarrollo web",
            "Frontend con React",
            "Backend con Node.js",
        ],
        "proyectos": ["Lleure Time", "FriendsGo"],
    },
    "Java": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Desarrollo backend",
            "Spring Boot",
            "Integración entre Java y procesos Python",
        ],
        "proyectos": ["LookR"],
    },
    "FastAPI": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "APIs REST",
            "Lógica de negocio",
            "Gestión de pipelines de automatización",
            "Integración de agentes y modelos locales",
        ],
        "proyectos": ["JobAgent", "LookR"],
    },
    "Express.js": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Diseño y desarrollo completo de backends",
            "APIs REST",
            "Autenticación JWT",
            "Integración con Socket.IO",
            "Testing de integración",
        ],
        "proyectos": ["Lleure Time", "FriendsGo"],
    },
    "Spring Boot": {
        "nivel": "básico-intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": ["Desarrollo de APIs y servicios backend durante la formación"],
        "proyectos": [],
    },
    "SQL": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "tecnologias": ["PostgreSQL", "MySQL", "SQLite"],
        "usos": [
            "Modelado relacional",
            "Normalización 3FN",
            "Definición de relaciones",
            "Consultas y persistencia",
        ],
        "proyectos": ["Lleure Time", "FriendsGo", "JobAgent"],
    },
    "MongoDB": {
        "nivel": "básico-intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": ["Persistencia documental durante la formación"],
        "proyectos": [],
    },
    "Pinecone": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Base de datos vectorial",
            "Namespaces por usuario",
            "Recuperación semántica y visual",
            "Indexación de embeddings",
        ],
        "proyectos": ["LookR"],
    },
    "Docker": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Contenedorización de servicios",
            "Despliegue local",
            "Homelab y self-hosting",
        ],
        "proyectos": ["JobAgent", "LookR", "Homelab"],
    },
    "n8n": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Orquestación de flujos automatizados",
            "Ejecución programada mediante cron",
            "Coordinación del pipeline de candidaturas",
        ],
        "proyectos": ["JobAgent"],
    },
    "Playwright": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Scraping de ofertas",
            "Extracción de formularios",
            "Automatización de navegación y cumplimentación",
        ],
        "proyectos": ["JobAgent"],
    },
    "Ollama": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Ejecución local de LLMs y VLMs",
            "Análisis semántico",
            "Generación de respuestas",
            "Agentes locales",
        ],
        "proyectos": ["JobAgent", "LookR"],
    },
    "PydanticAI": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Desarrollo de agentes",
            "Definición de salidas estructuradas",
            "Integración con modelos locales",
        ],
        "proyectos": ["LookR"],
    },
    "PyTorch": {
        "nivel": "básico-intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Formación en Machine Learning y Deep Learning",
            "Uso de modelos y tensores",
        ],
        "proyectos": [],
    },
    "Scikit-Learn": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Modelos clásicos de Machine Learning",
            "Preprocesamiento y evaluación",
        ],
        "proyectos": [],
    },
    "Socket.IO": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Chat en tiempo real",
            "Comentarios en tiempo real",
            "Señalización WebRTC",
            "Emparejamiento de videollamadas",
        ],
        "proyectos": ["FriendsGo"],
    },
    "WebRTC": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Videollamadas P2P",
            "Señalización mediante Socket.IO",
            "Configuración de servidores STUN/TURN",
            "Intercambio de SDP y candidatos ICE",
        ],
        "proyectos": ["FriendsGo"],
    },
    "Git": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Control de versiones",
            "Trabajo colaborativo",
            "Gestión de repositorios",
        ],
        "proyectos": ["Lleure Time", "FriendsGo", "JobAgent", "LookR"],
    },
    "Linux": {
        "nivel": "intermedio",
        "inicio_aproximado": None,
        "experiencia_aproximada": None,
        "usos": [
            "Administración de servidores locales",
            "Despliegue de servicios",
            "Automatización y self-hosting",
        ],
        "proyectos": ["JobAgent", "Homelab"],
    },
}

TECHNOLOGY_CONTEXT_INSTRUCTIONS = """
Usa esta información únicamente para responder preguntas sobre conocimientos,
experiencia práctica y tecnologías del candidato.

Reglas:
- No inventes años de experiencia.
- Si `experiencia_aproximada` es None, responde describiendo el uso práctico y
  los proyectos, sin convertirlo en una cifra.
- Diferencia experiencia profesional, experiencia académica y experiencia en
  proyectos personales.
- No afirmes dominio experto o avanzado salvo que esté indicado explícitamente.
- Prioriza respuestas breves, verificables y adaptadas a la pregunta.
"""
