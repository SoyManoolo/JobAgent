from pathlib import Path

content = '''CVS = {
    "backend_es": """
BACKEND DEVELOPER

ERIK MANUEL SALDAÑA DÍAZ

PERFIL PROFESIONAL

Desarrollador Backend especializado en el desarrollo de aplicaciones con Python (FastAPI), TypeScript (Express.js) y Java (Spring Boot). Experiencia en APIs REST, arquitecturas distribuidas y automatización con IA. Interesado en el desarrollo de software escalable y mantenible.

EXPERIENCIA

Lleure Time
Desarrollador Backend | 2024-2025

- Desarrollo completo del backend de una aplicación web con Express.js, TypeScript y Node.js.
- Diseño e implementación de una API REST, desarrollando la lógica de negocio, la autenticación mediante JWT y la comunicación con la base de datos.
- Modelado de la base de datos relacional en MySQL aplicando principios de normalización (3FN) y optimización de consultas.
- Implementación de pruebas automatizadas de integración con Jest y Supertest para validar los endpoints de la API.
- Colaboración en un equipo ágil siguiendo metodología Scrum e integración de servicios externos.

PROYECTOS

JobAgent

Sistema de automatización para el proceso de búsqueda y preparación de candidaturas de empleo. Diseñado como una arquitectura modular donde componentes especializados colaboran para extraer y analizar ofertas, seleccionar el CV más adecuado, generar respuestas asistidas por un LLM local y automatizar la cumplimentación de solicitudes, manteniendo siempre la revisión y aprobación del usuario antes del envío.

Tecnologías: FastAPI, SQLite, Playwright, Ollama, n8n, Docker.

LookR

Motor de búsqueda multimodal diseñado para localizar prendas mediante consultas en lenguaje natural, imágenes o una combinación de ambas. Responsable del diseño de la arquitectura backend y del sistema de recuperación vectorial, evaluando distintos LLMs y VLMs, desarrollando un agente basado en un LLM local, definiendo su lógica de decisión mediante ingeniería de prompts y configurando la recuperación vectorial sobre Pinecone.

Tecnologías: FastAPI, Pinecone, PydanticAI, Ollama, CLIP, Docker.

FriendsGo

Red social desarrollada sobre una arquitectura cliente-servidor con comunicación en tiempo real mediante Socket.IO y WebRTC para chat y videollamadas entre usuarios. Responsable del desarrollo completo del backend, incluyendo el diseño de la arquitectura, la API REST, el modelado de la base de datos, la autenticación mediante JWT y la infraestructura de señalización y servidores TURN/STUN para conexiones P2P.

Tecnologías: Express.js, PostgreSQL, Sequelize, Socket.IO, WebRTC, JWT, Docker.

FORMACIÓN

- Curso de Especialización en Inteligencia Artificial y Big Data | 2025-2026
- CFGS Desarrollo de Aplicaciones Web | 2023-2025

IDIOMAS

- Castellano: Nativo
- Catalán: Nativo
- Inglés: B2

CONTACTO

- Email: erik.saldi.diaz@gmail.com
- GitHub: https://github.com/SoyManoolo
- Ubicación: Barcelona, España
- Teléfono: +34 688 29 76 53
""",

    "backend_en": """
BACKEND DEVELOPER

ERIK MANUEL SALDAÑA DÍAZ

PROFESSIONAL PROFILE

Backend Developer specializing in application development using Python (FastAPI), TypeScript (Express.js), and Java (Spring Boot). Experienced in REST APIs, distributed architectures, and AI-driven automation. Interested in building scalable and maintainable software.

EXPERIENCE

Lleure Time
Backend Developer | 2024-2025

- Developed the complete backend of a web application using Express.js, TypeScript, and Node.js.
- Designed and implemented a REST API, developing the business logic, JWT-based authentication, and database communication.
- Modeled a MySQL relational database by applying Third Normal Form (3NF) principles and query optimization.
- Implemented automated integration tests with Jest and Supertest to validate API endpoints.
- Collaborated within an Agile Scrum team and integrated external services.

PROJECTS

JobAgent

Automation system for the job search and application process. Designed as a modular architecture where specialized components collaborate to extract and analyze job offers, select the most suitable CV, generate LLM-assisted responses, and automate application completion while keeping the user in control through a final review and approval step.

Technologies: FastAPI, SQLite, Playwright, Ollama, n8n, Docker.

LookR

Multimodal search engine designed to retrieve fashion items using natural language queries, images, or a combination of both. Responsible for designing the backend architecture and vector retrieval system, evaluating different LLMs and VLMs, developing a local LLM-based agent, defining its decision-making logic through prompt engineering, and configuring vector retrieval on Pinecone.

Technologies: FastAPI, Pinecone, PydanticAI, Ollama, CLIP, Docker.

FriendsGo

Social networking platform built on a client-server architecture featuring real-time communication through Socket.IO and WebRTC for chat and peer-to-peer video calls. Responsible for the complete backend development, including the system architecture, REST API, relational database design, JWT-based authentication, and the signaling infrastructure and TURN/STUN servers required for peer-to-peer connections.

Technologies: Express.js, PostgreSQL, Sequelize, Socket.IO, WebRTC, JWT, Docker.

EDUCATION

- Specialization Course in Artificial Intelligence and Big Data | 2025-2026
- Higher Technician in Web Application Development | 2023-2025

LANGUAGES

- Spanish: Native
- Catalan: Native
- English: B2

CONTACT

- Email: erik.saldi.diaz@gmail.com
- GitHub: https://github.com/SoyManoolo
- Location: Barcelona, Spain
- Phone: +34 688 29 76 53
""",

    "ia_es": """
INGENIERO DE IA JUNIOR

ERIK MANUEL SALDAÑA DÍAZ

PERFIL PROFESIONAL

Ingeniero de IA Junior especializado en el desarrollo de soluciones basadas en modelos de lenguaje, agentes inteligentes y sistemas de recuperación de información. Experiencia en el diseño de aplicaciones que integran LLMs locales, búsqueda vectorial, automatización de procesos y arquitecturas backend escalables, con interés en la IA aplicada y el aprendizaje continuo.

EXPERIENCIA

Lleure Time
Desarrollador Backend | 2024-2025

- Desarrollo completo del backend de una aplicación web con Express.js, TypeScript y Node.js.
- Diseño e implementación de una API REST, desarrollando la lógica de negocio, la autenticación mediante JWT y la comunicación con la base de datos.
- Modelado de la base de datos relacional en MySQL aplicando principios de normalización (3FN) y optimización de consultas.
- Implementación de pruebas automatizadas de integración con Jest y Supertest para validar los endpoints de la API.
- Colaboración en un equipo ágil siguiendo metodología Scrum e integración de servicios externos.

PROYECTOS

JobAgent

Sistema de automatización del proceso de candidatura a ofertas de empleo. Diseñado como una arquitectura modular donde componentes especializados colaboran para extraer y analizar ofertas, seleccionar el CV más adecuado, generar respuestas asistidas por un LLM local y automatizar la cumplimentación de solicitudes, manteniendo siempre la revisión y aprobación del usuario antes del envío.

Tecnologías: FastAPI, SQLite, Playwright, Ollama, n8n, Docker.

LookR

Motor de búsqueda multimodal diseñado para localizar prendas mediante consultas en lenguaje natural, imágenes o una combinación de ambas. Responsable del diseño de la arquitectura backend y del sistema de recuperación vectorial, evaluando distintos LLMs y VLMs, desarrollando un agente basado en un LLM local, definiendo su lógica de decisión mediante ingeniería de prompts y configurando la recuperación vectorial sobre Pinecone.

Tecnologías: FastAPI, Pinecone, PydanticAI, Ollama, CLIP, Docker.

FriendsGo

Red social desarrollada sobre una arquitectura cliente-servidor con comunicación en tiempo real mediante Socket.IO y WebRTC para chat y videollamadas entre usuarios. Responsable del desarrollo completo del backend, incluyendo el diseño de la arquitectura, la API REST, el modelado de la base de datos, la autenticación mediante JWT y la infraestructura de señalización y servidores TURN/STUN para conexiones P2P.

Tecnologías: Express.js, PostgreSQL, Sequelize, Socket.IO, WebRTC, JWT, Docker.

FORMACIÓN

- Curso de Especialización en Inteligencia Artificial y Big Data | 2025-2026
- CFGS Desarrollo de Aplicaciones Web | 2023-2025

IDIOMAS

- Castellano: Nativo
- Catalán: Nativo
- Inglés: B2

CONTACTO

- Email: erik.saldi.diaz@gmail.com
- GitHub: https://github.com/SoyManoolo
- Ubicación: Barcelona, España
- Teléfono: +34 688 29 76 53
""",

    "ia_en": """
JUNIOR AI ENGINEER

ERIK MANUEL SALDAÑA DÍAZ

PROFESSIONAL PROFILE

Junior AI Engineer specializing in the development of solutions based on large language models, intelligent agents, and information retrieval systems. Experienced in designing applications that integrate local LLMs, vector search, process automation, and scalable backend architectures, with a strong interest in applied AI and continuous learning.

EXPERIENCE

Lleure Time
Backend Developer | 2024-2025

- Developed the complete backend of a web application using Express.js, TypeScript, and Node.js.
- Designed and implemented a REST API, developing the business logic, JWT-based authentication, and database communication.
- Modeled a MySQL relational database by applying Third Normal Form (3NF) principles and query optimization.
- Implemented automated integration tests with Jest and Supertest to validate API endpoints.
- Collaborated within an Agile Scrum team and integrated external services.

PROJECTS

JobAgent

Automation system for the job application process. Designed as a modular architecture where specialized components collaborate to extract and analyze job offers, select the most suitable CV, generate LLM-assisted responses, and automate application completion while keeping the user in control through a final review and approval step.

Technologies: FastAPI, SQLite, Playwright, Ollama, n8n, Docker.

LookR

Multimodal search engine designed to retrieve fashion items using natural language queries, images, or a combination of both. Responsible for designing the backend architecture and vector retrieval system, evaluating different LLMs and VLMs, developing a local LLM-based agent, defining its decision-making logic through prompt engineering, and configuring vector retrieval on Pinecone.

Technologies: FastAPI, Pinecone, PydanticAI, Ollama, CLIP, Docker.

FriendsGo

Social networking platform built on a client-server architecture featuring real-time communication through Socket.IO and WebRTC for chat and peer-to-peer video calls. Responsible for the complete backend development, including the system architecture, REST API, relational database design, JWT-based authentication, and the signaling infrastructure and TURN/STUN servers required for peer-to-peer connections.

Technologies: Express.js, PostgreSQL, Sequelize, Socket.IO, WebRTC, JWT, Docker.

EDUCATION

- Specialization Course in Artificial Intelligence and Big Data | 2025-2026
- Higher Technician in Web Application Development | 2023-2025

LANGUAGES

- Spanish: Native
- Catalan: Native
- English: B2

CONTACT

- Email: erik.saldi.diaz@gmail.com
- GitHub: https://github.com/SoyManoolo
- Location: Barcelona, Spain
- Phone: +34 688 29 76 53
"""
}
'''

path = Path("/mnt/data/cvs_simple.py")
path.write_text(content, encoding="utf-8")
print(f"Creado: {path}")
