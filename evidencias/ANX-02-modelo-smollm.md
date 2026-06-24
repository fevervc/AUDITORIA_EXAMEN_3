# ANEXO 2 – Evidencia: Modelo LLM smollm:360m en Ollama

**Fecha de captura:** 24/06/2026  
**Responsable:** Equipo Auditor  
**Herramienta:** Ollama CLI  

## Descripción

Se verificó que el modelo `smollm:360m` está disponible en Ollama y es el modelo configurado en el backend del sistema.

## Resultado del Comando `ollama list`

```
NAME           ID              SIZE      MODIFIED
smollm:360m    b3ba1ccba2b8    229 MB    20 minutes ago
```

## Verificación desde el Contenedor Docker

Se ejecutó una consulta HTTP desde dentro del contenedor backend a `http://host.docker.internal:11434/api/tags`:

```json
{
  "models": [{
    "name": "smollm:360m",
    "model": "smollm:360m",
    "modified_at": "2026-06-24T15:38:00.776-05:00",
    "size": 229131061,
    "digest": "b3ba1ccba2b80fe98c3b00798a95228d709b6ba86f15b483a4011b05fa2afe29",
    "details": {
      "format": "gguf",
      "family": "llama",
      "parameter_size": "361.82M",
      "quantization_level": "Q4_0",
      "context_length": 2048,
      "embedding_length": 960
    },
    "capabilities": ["completion"]
  }]
}
```

## Configuración en Backend (`main.py`)

```python
llm = OllamaLLM(model="smollm:360m", temperature=0, base_url="http://host.docker.internal:11434")
```

## Análisis

| Parámetro         | Valor              |
|-------------------|--------------------|
| Modelo            | smollm:360m        |
| Parámetros        | 361.82M            |
| Cuantización      | Q4_0 (4-bit)       |
| Ventana contexto  | 2048 tokens        |
| Formato           | GGUF               |
| Temperatura       | 0 (determinista)   |

## Hallazgo

El modelo `smollm:360m` es un modelo de lenguaje muy compacto (361M parámetros). Aunque funcional para clasificación de intenciones básicas, sus respuestas RAG presentan calidad limitada comparado con modelos más grandes como `llama3.1:8b`, lo que representa un riesgo en la precisión de respuestas al usuario.

---
*Evidencia generada durante la Auditoría de Sistemas – CORPORATE EPIS PILOT*
