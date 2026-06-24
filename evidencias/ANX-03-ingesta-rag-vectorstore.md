# ANEXO 3 – Evidencia: Ingesta de Documentos y Base Vectorial (RAG)

**Fecha de captura:** 24/06/2026  
**Responsable:** Equipo Auditor  
**Herramienta:** Docker Build Logs  

## Descripción

Durante el proceso de construcción del contenedor Docker del backend, se ejecutó el script `ingest.py` que carga los documentos de la base de conocimiento, genera embeddings con el modelo `intfloat/multilingual-e5-large` y los almacena en ChromaDB.

## Salida del Script de Ingesta (durante `docker build`)

```
--- INICIO DEL SCRIPT DE INGESTA ---

1a. Cargando documentos PDF...
  0%|          | 0/3 [00:00<?, ?it/s]100%|██████████| 3/3 [00:00<00:00, 35.87it/s]

1b. Cargando documentos de texto (.txt)...
  0%|          | 0/3 [00:00<?, ?it/s]100%|██████████| 3/3 [00:00<00:00, 17355.74it/s]

¡Éxito! Se cargaron un total de 7 documentos.

2. Dividiendo documentos en chunks...
Se dividieron en 13 chunks.

3. Generando embeddings con el modelo 'multilingual-e5-large'...

4. Creando base de datos vectorial en 'vector_store'...
Eliminando la antigua base de datos vectorial en 'vector_store'...

--- ¡INGESTA COMPLETADA EXITOSAMENTE! ---
```

## Documentos en la Base de Conocimiento

| Archivo                     | Tipo  | Contenido                                |
|-----------------------------|-------|------------------------------------------|
| Contacto_acme.pdf           | PDF   | Directorio de contactos ACME Corp        |
| Empresa_ACME.pdf            | PDF   | Información corporativa ACME             |
| guia_soporte_red.pdf        | PDF   | Guía técnica de soporte de red           |
| politica_teletrabajo.txt    | TXT   | Política de teletrabajo                  |
| procedimientos_internos.txt | TXT   | Procedimientos internos de soporte       |
| producto_anviltron.txt      | TXT   | Información del producto Anviltron       |

**Total:** 7 documentos → 13 chunks vectorizados en ChromaDB

## Modelo de Embeddings

- **Modelo:** `intfloat/multilingual-e5-large`
- **Tipo:** HuggingFace Sentence Transformer
- **Capacidad:** Multilingüe (incluye español)
- **Almacenamiento:** ChromaDB (directorio `vector_store/`)

## Conclusión

La base vectorial fue construida exitosamente. El sistema RAG está operativo y puede recuperar contexto relevante de la base de conocimiento antes de generar respuestas.

---
*Evidencia generada durante la Auditoría de Sistemas – CORPORATE EPIS PILOT*
