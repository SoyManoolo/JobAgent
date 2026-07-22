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

### `POST /scraper/linkedin/easyapply/{id}`

Extrae las preguntas de Easy Apply de una oferta concreta. Si la solicitud ya no está disponible, la oferta se elimina lógicamente. Actualmente el proceso solo extrae preguntas: no rellena campos ni selecciona o sube el CV.

**Respuesta `200`**

```json
{
  "oferta_id": "bf3877ce-cc2d-4c57-a1eb-05d4048899a5",
  "disponible": true,
  "total_preguntas": 1,
  "preguntas": [
    {
      "pregunta_id": "input-123",
      "texto": "¿Cuántos años de experiencia tienes?",
      "tipo": "number",
      "obligatoria": true,
      "selector_temporal": "#input-123",
      "opciones": []
    }
  ],
  "actualizada": true
}
```

`pregunta_id` sí se genera durante la extracción y permite asociar cada respuesta a su campo. `selector_temporal` solo sirve durante la sesión de navegador en que se detectó: puede aparecer en la respuesta inmediata de extracción, pero no se persiste ni es reutilizable en sesiones posteriores.

### Portales aún no implementados

`POST /scraper/infojobs`, `POST /scraper/indeed` y `POST /scraper/glassdoor` son placeholders no funcionales; actualmente devuelven una cadena vacía y no extraen ofertas.

## Agente IA

### `POST /agent/ofertas/procesar`

Analiza hasta 25 ofertas en estado `extraida` mediante Ollama. Actualiza cada una a `analizada`, `descartada` o `error`.

**Respuesta `200`**

```json
{"total":12,"procesadas":11,"errores":1}
```

### `POST /agent/ofertas/responder`

Genera respuestas para hasta 25 ofertas en `pendientes_respuestas`. Una oferta pasa a `lista_para_aplicar` si todas sus preguntas obligatorias tienen respuesta suficiente.

**Respuesta `200`**

```json
{"total":3,"procesadas":3,"errores":0}
```

### `POST /agent/ofertas/{id}/responder`

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
  }
}
```

Si no se encuentra la oferta o el procesamiento falla, la implementación actual devuelve `{"error":"..."}` con estado HTTP `200`; los clientes deben comprobar ese campo. Esto es una limitación temporal: se sustituirá por códigos HTTP adecuados cuando se mejore el manejo de errores.

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

Devuelve contadores de ofertas activas.

**Respuesta `200`**

```json
{"total_ofertas":42,"aplicadas":5,"descartadas":12}
```

### `PATCH /dashboard/ofertas/{id}/notas`

Actualiza exclusivamente las notas de una oferta. El valor debe ir envuelto en la clave `notas`.

```bash
curl -X PATCH 'http://127.0.0.1:8000/api/v1/dashboard/ofertas/bf3877ce-cc2d-4c57-a1eb-05d4048899a5/notas' \
  -H 'Content-Type: application/json' \
  -d '{"notas":"Revisar requisitos de inglés"}'
```

- `200`: oferta actualizada.
- `404`: `{"detail":"Oferta no encontrada"}`.
