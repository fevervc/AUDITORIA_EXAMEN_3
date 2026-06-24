# ANEXO 6 – Evidencia: Revisión de Código Fuente y Arquitectura

**Fecha de captura:** 24/06/2026  
**Responsable:** Equipo Auditor  
**Herramienta:** Revisión estática de código  

## Descripción

Se realizó una revisión estática del código fuente del sistema para evaluar calidad, seguridad y adherencia a buenas prácticas.

---

## Estructura del Proyecto

```
AuditoriaHelpDeskIA/
├── backend/
│   ├── Dockerfile              # Imagen Python 3.12-slim
│   ├── main.py                 # API FastAPI + LangChain
│   ├── ingest.py               # Script de ingesta RAG
│   ├── database_setup.py       # Inicialización SQLite
│   ├── requirements.txt        # Dependencias Python
│   ├── knowledge_base/         # Documentos fuente
│   └── vector_store/           # ChromaDB persistido
├── frontend/
│   ├── Dockerfile              # Build Node + Nginx
│   ├── src/App.tsx             # Lógica de estado del chat
│   └── src/components/         # Componentes React
├── nginx/
│   └── nginx.conf              # Proxy inverso
├── docker-compose.yml          # Orquestación de servicios
└── kubernetes/                 # Manifiestos K8s
```

---

## Hallazgos de Revisión de Código

### H-01: CORS configurado con comodín (Criticidad: Media)
```python
# main.py línea 45-48
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ⚠️ Permite cualquier origen
    allow_credentials=False,
    ...
)
```
**Riesgo:** Permite solicitudes desde cualquier dominio, exponiendo la API a ataques CSRF en entornos de producción.  
**Recomendación:** Definir dominios específicos permitidos.

### H-02: Sin autenticación en endpoints (Criticidad: Alta)
```python
@app.get("/ask")
def ask_question(question: str):  # Sin token/autenticación
```
**Riesgo:** Cualquier cliente puede consumir la API sin autenticarse, lo que podría abusar del servicio LLM.  
**Recomendación:** Implementar API Key o JWT en los endpoints.

### H-03: SQLite sin cifrado (Criticidad: Media)
**Riesgo:** La base de datos de tickets no está cifrada. Si el archivo `tickets.db` es accesible, los datos de soporte quedan expuestos.  
**Recomendación:** Migrar a PostgreSQL o implementar cifrado a nivel de archivo.

### H-04: Volumen de DB montado desde host sin inicialización (Criticidad: Alta)
```yaml
# docker-compose.yml
- ./backend/tickets.db:/app/tickets.db  # Archivo de 0 bytes en host
```
**Riesgo:** El archivo host vacío sobrescribe la BD inicializada en el contenedor, causando error `no such table: tickets`.  
**Corrección aplicada:** Ejecutar `python database_setup.py` en el contenedor activo.  
**Recomendación Permanente:** Usar un volumen nombrado de Docker en lugar de bind mount.

### H-05: Logging en modo DEBUG sin filtrado (Criticidad: Baja)
**Riesgo:** Los logs incluyen detalles de todas las peticiones HTTP a Ollama en nivel DEBUG, lo que puede exponer información sensible en producción.  
**Recomendación:** Configurar el nivel de log en INFO para producción.

---

## Fortalezas Identificadas

| Aspecto                      | Evaluación |
|------------------------------|------------|
| Arquitectura RAG implementada| ✅ Buena práctica |
| Router de intenciones LLM    | ✅ Patrón robusto |
| Monitorización Prometheus    | ✅ Buena práctica DevOps |
| Logging estructurado (loguru)| ✅ Trazabilidad adecuada |
| Separación frontend/backend  | ✅ Arquitectura desacoplada |
| CI/CD con GitHub Actions     | ✅ Automatización implementada |
| Manifiestos Kubernetes       | ✅ Listo para producción |

---
*Evidencia generada durante la Auditoría de Sistemas – CORPORATE EPIS PILOT*
