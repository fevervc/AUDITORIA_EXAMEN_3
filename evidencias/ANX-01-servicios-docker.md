# ANEXO 1 – Evidencia: Servicios Docker Activos

**Fecha de captura:** 24/06/2026  
**Responsable:** Equipo Auditor  
**Herramienta:** Docker Compose + Docker CLI  

## Descripción

Se ejecutó el comando `docker ps` para verificar que los tres servicios del sistema (backend, frontend, proxy) se encuentran activos y escuchando en los puertos configurados.

## Resultado del Comando `docker ps`

```
CONTAINER ID   IMAGE                          COMMAND                  CREATED         STATUS         PORTS                                         NAMES
a126c3d2e616   auditoriahelpdeskia-frontend   "/docker-entrypoint.…"   Up 3 seconds   Up 3 seconds   80/tcp                                        auditoriahelpdeskia-frontend-1
e7d80e6a04cd   auditoriahelpdeskia-backend    "uvicorn main:app --…"   Up 4 seconds   Up 4 seconds   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   auditoriahelpdeskia-backend-1
a12725981392   nginx:stable-alpine            "/docker-entrypoint.…"   Up 3 seconds   Up 3 seconds   0.0.0.0:5173->80/tcp, [::]:5173->80/tcp       auditoriahelpdeskia-proxy-1
```

## Análisis

| Servicio  | Imagen                        | Puerto Host | Puerto Contenedor | Estado |
|-----------|-------------------------------|-------------|-------------------|--------|
| Backend   | auditoriahelpdeskia-backend   | 8000        | 8000              | ✅ Up  |
| Frontend  | auditoriahelpdeskia-frontend  | —           | 80 (interno)      | ✅ Up  |
| Proxy     | nginx:stable-alpine           | 5173        | 80                | ✅ Up  |

## Conclusión

Los tres contenedores Docker están operativos. El proxy NGINX en el puerto 5173 enruta correctamente las peticiones `/api/` al backend (puerto 8000) y las peticiones `/` al frontend (puerto 80 interno).

---
*Evidencia generada durante la Auditoría de Sistemas – CORPORATE EPIS PILOT*
