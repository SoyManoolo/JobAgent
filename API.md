# API de JobAgent

Base URL local: `http://127.0.0.1:8000/api/v1`

La especificación interactiva generada por FastAPI está disponible en `http://127.0.0.1:8000/docs` cuando el servidor está en ejecución.

## Convenciones

- Las rutas de ofertas se escriben con barra final: `/ofertas/`.
- Los identificadores de oferta son UUID generados al guardar una extracción.
- `DELETE` realiza borrado lógico: la oferta deja de aparecer en las consultas normales.
- Los enums válidos son:
  - `estado`: `extraida`, `analizada`, `pendientes_respuestas`, `lista_para_aplicar`, `aplicada`, `descartada`, `error`.
  - `perfil`: `backend`, `ia`, `desconocido`.
- Las llamadas a Ollama y las ejecuciones del scraper se reintentan hasta tres veces ante errores transitorios. Se puede configurar mediante `RETRY_ATTEMPTS` y el tiempo de espera incremental mediante `RETRY_DELAY_SECONDS` (en segundos).

## Estado del servicio

### `GET /`

Comprueba que la API está disponible. Esta ruta no lleva el prefijo `/api/v1`.

**Respuesta `200`**

```json
{"status":"JobAgent API running successfully"}
```

## Scraper

### `POST /scraper/linkedin`

Extrae ofertas de LinkedIn para una búsqueda y guarda las no duplicadas con estado `extraida`.

| Query parameter | Tipo | Predeterminado |
| --- | --- | --- |
| `busqueda` | string | `Backend` |

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/scraper/linkedin?busqueda=Backend'
```

**Respuesta `200`**

```json
{
  "busqueda": "Backend",
  "ofertas_extraidas": 18,
  "ofertas_guardadas": 12,
  "ofertas_no_guardadas": 0,
  "ofertas_duplicadas": 6
}
```

### `POST /scraper/linkedin/easyapply/procesar`

Busca ofertas analizadas con Solicitud sencilla sin preguntas almacenadas y extrae sus formularios.

| Query parameter | Tipo | Predeterminado |
| --- | --- | --- |
| `limite` | integer | `10` |

**Respuesta `200`**

```json
{
  "total": 1,
  "resultados": [
    {
      "oferta_id": "bf3877ce-cc2d-4c57-a1eb-05d4048899a5",
      "disponible": true,
      "total_preguntas": 0,
      "preguntas": [],
      "actualizada": true
    }
  ]
}
```

### `POST /scraper/linkedin/easyapply/procesar/{id}`

Extrae y guarda las preguntas de Easy Apply de una única oferta identificada por su UUID. Si no hay preguntas adicionales, la oferta pasa a `lista_para_aplicar`; si las hay, pasa a `pendientes_respuestas`. Si LinkedIn informa de que la solicitud ya no está disponible, la oferta pasa a `error` para revisión manual.

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/scraper/linkedin/easyapply/procesar/bf3877ce-cc2d-4c57-a1eb-05d4048899a5'
```

**Respuesta `200`**

```json
{
  "oferta_id": "bf3877ce-cc2d-4c57-a1eb-05d4048899a5",
  "disponible": true,
  "total_preguntas": 0,
  "preguntas": [],
  "actualizada": true
}
```

La respuesta incluye las preguntas detectadas. `selector_temporal`, si aparece, solo es válido durante la sesión de navegador que realizó la extracción y no se persiste.

### `POST /scraper/linkedin/easyapply/aplicar/{id}`

Rellena y envía mediante Playwright una solicitud de LinkedIn Easy Apply que ya ha sido revisada. La oferta debe estar en estado `lista_para_aplicar`, pertenecer a LinkedIn y tener respuestas suficientes para todas sus preguntas obligatorias.

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/scraper/linkedin/easyapply/aplicar/bf3877ce-cc2d-4c57-a1eb-05d4048899a5'
```

**Respuesta `200`**

```json
{
  "oferta_id": "bf3877ce-cc2d-4c57-a1eb-05d4048899a5",
  "enviada": true,
  "ya_enviada": false,
  "campos_rellenados": 3,
  "cv_seleccionado": "CV_EN_BACKEND.pdf",
  "estado": "aplicada"
}
```

Tras detectar la confirmación de LinkedIn, guarda el estado `aplicada` y `fecha_aplicacion`. Si LinkedIn ya muestra la solicitud como enviada, sincroniza igualmente el estado local.

- `404`: la oferta no existe o está eliminada.
- `409`: la oferta no es de LinkedIn Easy Apply, no está lista para aplicar o tiene respuestas obligatorias incompletas.
- `500`: el formulario cambió, LinkedIn rechazó algún campo o no se pudo confirmar el envío.

Este endpoint realiza el envío real de la candidatura. No aplica reintentos automáticos sobre la operación completa para evitar solicitudes duplicadas después de un resultado ambiguo.

Rellena campos `text`, `number`, `radio` y `select`, y selecciona explícitamente el CV configurado para el `perfil_recomendado` e `idioma_oferta`. Los nombres de los documentos de LinkedIn se definen de forma privada en `agent/prompts/cv.py`, mediante `CVS_LINKEDIN`; consulta `cv.example.py` como plantilla. Si no hay una configuración correspondiente, devuelve `409` y no envía la solicitud. La subida de CV y otros tipos de campo quedan pendientes de incorporar.

### Portales aún no implementados

`POST /scraper/infojobs`, `POST /scraper/indeed` y `POST /scraper/glassdoor` son placeholders no funcionales; actualmente devuelven una cadena vacía y no extraen ofertas.

## Agente IA

### `POST /agent/ofertas/procesar`

Analiza hasta el número indicado de ofertas en estado `extraida` mediante Ollama. Actualiza cada una a `analizada`, `descartada` o `error`. Si hay menos ofertas disponibles que el límite solicitado, procesa únicamente las disponibles sin devolver error.

| Query parameter | Tipo | Predeterminado | Descripción |
| --- | --- | --- | --- |
| `limite` | integer | `25` | Número máximo de ofertas que se analizarán. |

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/agent/ofertas/procesar?limite=50'
```

**Respuesta `200`**

```json
{"total":12,"procesadas":11,"errores":1}
```

Si ya existe un análisis por lote o individual en ejecución, devuelve `409` con
`{"detail":"Ya hay un análisis de ofertas en curso"}`. No inicia una segunda
petición a Ollama.

### `POST /agent/ofertas/procesar/{id}`

Analiza una única oferta activa identificada por su UUID mediante Ollama. Guarda los datos de clasificación y actualiza su estado a `analizada` o `descartada` según el resultado. Si el análisis falla, la oferta queda en estado `error` y la API responde con un error `500`.

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/agent/ofertas/procesar/bf3877ce-cc2d-4c57-a1eb-05d4048899a5'
```

**Respuesta `200`**

```json
{
  "id": "bf3877ce-cc2d-4c57-a1eb-05d4048899a5",
  "estado": "analizada",
  "perfil_recomendado": "backend",
  "idioma_oferta": "es",
  "seniority": "junior",
  "score_backend": 85,
  "score_ia": 25,
  "score_encaje": 82,
  "resumen": "Oferta de desarrollo backend con Python y FastAPI.",
  "motivo_encaje": "Buen encaje por el stack y un nivel de experiencia accesible."
}
```

- `404`: `{"detail":"Oferta no encontrada"}`. También se devuelve para ofertas eliminadas lógicamente.
- `409`: ya hay otro análisis de ofertas en curso.
- `500`: no se pudo completar el análisis; la oferta queda marcada como `error`.

### `POST /agent/ofertas/responder`

Genera respuestas para hasta el número indicado de ofertas en `pendientes_respuestas`. Si todas las preguntas obligatorias reciben una respuesta válida, la oferta pasa a `lista_para_aplicar`; si queda alguna sin resolver, permanece en `pendientes_respuestas`.

Todos los endpoints del agente comparten una única reserva de Ollama. Si otro
análisis o generación de respuestas está activo, el endpoint devuelve `409` con
`{"detail":"Ollama ya está procesando otra tarea"}`.

| Query parameter | Tipo | Predeterminado | Descripción |
| --- | --- | --- | --- |
| `limite` | integer | `5` | Número máximo de ofertas para las que se generarán respuestas. Admite valores entre `1` y `100`. |

```bash
curl -X POST 'http://127.0.0.1:8000/api/v1/agent/ofertas/responder?limite=5'
```

**Respuesta `200`**

```json
{"total":3,"procesadas":3,"errores":0}
```

### `POST /agent/ofertas/responder/{id}`

Genera y guarda las respuestas de una única oferta.

**Respuesta `200`**

```json
{
  "respuestas": {
    "respuestas": [
      {
        "pregunta_id": "input-123",
        "informacion_suficiente": true,
        "respuesta": "3",
        "valor_seleccionado": null
      }
    ]
  },
  "estado": "lista_para_aplicar"
}
```

Errores del endpoint individual:

- `404`: la oferta no existe.
- `409`: la oferta no tiene perfil o idioma válidos para seleccionar el CV.
- `502`: Ollama respondió, pero su JSON o sus respuestas no cumplen el contrato del formulario.
- `503`: Ollama no respondió después de agotar los reintentos.

## Ofertas

### `GET /ofertas/`

Devuelve ofertas no eliminadas, ordenadas de forma descendente por identificador en la implementación actual.

| Query parameter | Tipo | Predeterminado | Descripción |
| --- | --- | --- | --- |
| `pagina` | integer | `1` | Página solicitada. |
| `limite` | integer | `10` | Resultados por página. |
| `estado` | enum | — | Filtra por estado. |
| `perfil` | enum | — | Filtra por perfil recomendado. |
| `score_min` | integer | — | Encaje mínimo. |
| `empresa` | string | — | Coincidencia parcial, sin distinción de mayúsculas. |
| `aplicacion_sencilla` | boolean | — | Filtra por Easy Apply. |

```bash
curl 'http://127.0.0.1:8000/api/v1/ofertas/?estado=analizada&score_min=70'
```

**Respuesta `200`**

```json
{
  "total": 1,
  "pagina": 1,
  "limite": 10,
  "resultados": [
    {
      "id": "bf3877ce-cc2d-4c57-a1eb-05d4048899a5",
      "plataforma": "linkedin",
      "titulo": "Backend Developer",
      "empresa": "Acme",
      "estado": "analizada",
      "perfil_recomendado": "backend",
      "score_encaje": 82,
      "aplicacion_sencilla": true
    }
  ]
}
```

Las respuestas incluyen el resto de atributos persistidos de la oferta: URL, descripción, ubicación, salario, fechas, puntuaciones, resumen, motivo de encaje, preguntas, respuestas y notas cuando existan.

### `GET /ofertas/{id}`

Obtiene una oferta por UUID.

- `200`: objeto de oferta.
- `404`: `{"detail":"Oferta no encontrada"}`.

### `PATCH /ofertas/{id}/respuestas/{pregunta_id}`

Edita una sola respuesta de formulario. El dashboard puede usar este endpoint tanto para corregir una propuesta del LLM como para responder una pregunta directamente. No hay que enviar el JSON completo de respuestas.

Para preguntas `text` o `number`, envía `respuesta`:

```json
{"respuesta":"25000"}
```

Para preguntas `radio` o `select`, envía el valor de una opción permitida; la API guarda automáticamente el texto asociado:

```json
{"valor_seleccionado":"Yes"}
```

La respuesta incluye `todas_obligatorias_resueltas`, útil para que el dashboard habilite el botón de confirmación.

- `404`: oferta inexistente o eliminada.
- `422`: pregunta inexistente, campo incorrecto u opción no válida.

### `POST /ofertas/{id}/respuestas/confirmar`

Confirma las respuestas revisadas. Comprueba todas las preguntas obligatorias y cambia el estado a `lista_para_aplicar`.

- `200`: oferta confirmada.
- `404`: oferta inexistente o eliminada.
- `409`: la oferta no está pendiente de respuestas o queda alguna respuesta obligatoria inválida.

### `PATCH /ofertas/{id}`

Actualmente recibe un objeto libre y actualiza sus claves directamente; no existe todavía un esquema `OfertaUpdate` que limite los campos permitidos. Cuando se implemente, este endpoint documentará exclusivamente los campos autorizados —previsiblemente `estado` y `notas`— y sus validaciones.

```bash
curl -X PATCH 'http://127.0.0.1:8000/api/v1/ofertas/bf3877ce-cc2d-4c57-a1eb-05d4048899a5' \
  -H 'Content-Type: application/json' \
  -d '{"estado":"aplicada","notas":"Solicitud enviada el 22 de julio"}'
```

- `200`: oferta actualizada.
- `404`: `{"detail":"Oferta no encontrada"}`.

### `DELETE /ofertas/{id}`

Marca una oferta como eliminada; no borra físicamente su registro.

- `200`: oferta marcada como eliminada.
- `404`: `{"detail":"Oferta no encontrada"}`.

## Dashboard

### `GET /dashboard/stats`

Devuelve métricas de las ofertas no eliminadas: embudo por estado, trabajo pendiente, puntuaciones de encaje, Easy Apply, perfil recomendado, plataforma y tasa de aplicación.

**Respuesta `200`**

```json
{
  "total_ofertas": 42,
  "aplicadas": 5,
  "descartadas": 12,
  "por_estado": {
    "extraida": 4,
    "analizada": 10,
    "pendientes_respuestas": 3,
    "lista_para_aplicar": 8,
    "aplicada": 5,
    "descartada": 12,
    "error": 0
  },
  "pendientes": {
    "analisis": 4,
    "respuestas": 3,
    "listas_para_aplicar": 8
  },
  "ofertas_prioritarias": {"score_minimo": 70, "total": 9},
  "score_encaje": {
    "ofertas_evaluadas": 30,
    "medio": 57.4,
    "minimo": 8,
    "maximo": 94,
    "por_rango": {"0_19": 6, "20_39": 5, "40_59": 7, "60_79": 6, "80_100": 6}
  },
  "easy_apply": {
    "total": 20,
    "pendientes_preguntas": 4,
    "pendientes_respuestas": 3,
    "listas_para_aplicar": 5
  },
  "por_perfil": {"backend": 18, "ia": 8, "desconocido": 4, "sin_clasificar": 12},
  "por_plataforma": {"linkedin": 42},
  "tasa_aplicacion": 11.9
}
```

`ofertas_prioritarias` contabiliza ofertas con encaje de 70 o más que están analizadas, pendientes de respuesta o listas para aplicar. `tasa_aplicacion` es el porcentaje de ofertas aplicadas respecto al total activo.

### `PATCH /dashboard/ofertas/{id}/notas`

Actualiza exclusivamente las notas de una oferta. El valor debe ir envuelto en la clave `notas`.

```bash
curl -X PATCH 'http://127.0.0.1:8000/api/v1/dashboard/ofertas/bf3877ce-cc2d-4c57-a1eb-05d4048899a5/notas' \
  -H 'Content-Type: application/json' \
  -d '{"notas":"Revisar requisitos de inglés"}'
```

- `200`: oferta actualizada.
- `404`: `{"detail":"Oferta no encontrada"}`.
