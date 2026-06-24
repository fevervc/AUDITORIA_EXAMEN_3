# ANEXO 4 – Evidencia: Creación de Ticket de Soporte en Base de Datos

**Fecha de captura:** 24/06/2026  
**Responsable:** Equipo Auditor  
**Herramienta:** API REST del Backend + SQLite  

## Descripción

Se verificó el flujo completo de creación de tickets de soporte a través de la API del sistema y su persistencia en la base de datos SQLite.

## Prueba 1: Solicitud de Creación de Ticket vía API

**Comando ejecutado:**
```powershell
$encoded = [System.Uri]::EscapeDataString("ACTION_CREATE_TICKET:Router del segundo piso apagandose constantemente")
Invoke-RestMethod -Uri "http://localhost:8000/ask?question=$encoded"
```

**Respuesta del sistema:**
```json
{
  "answer": "De acuerdo. He creado el ticket de soporte #1 con tu problema: 'Router del segundo piso apagandose constantemente'. El equipo técnico se pondrá en contacto contigo.",
  "follow_up_required": false
}
```

## Prueba 2: Verificación en Base de Datos SQLite

**Comando ejecutado:**
```bash
docker compose exec backend python -c "
import sqlite3
conn = sqlite3.connect('tickets.db')
rows = conn.execute('SELECT * FROM tickets').fetchall()
conn.close()
print(rows)
"
```

**Resultado:**
```
[(1, 'Router del segundo piso apagandose constantemente', 'Abierto')]
```

## Estado de la Base de Datos

| ID | Descripción                                            | Estado  |
|----|--------------------------------------------------------|---------|
| 1  | Router del segundo piso apagandose constantemente      | Abierto |

## Flujo Verificado

```
Usuario describe problema
        ↓
Frontend captura texto y envía "ACTION_CREATE_TICKET:{descripcion}"
        ↓
Backend detecta el prefijo ACTION_CREATE_TICKET
        ↓
Función create_support_ticket() inserta en SQLite
        ↓
Se retorna ID del ticket creado
        ↓
Usuario recibe confirmación con número de ticket
```

## Problema Detectado (Hallazgo de Auditoría)

**Causa raíz del error inicial `no such table: tickets`:**  
El archivo `./backend/tickets.db` en el host era de 0 bytes (vacío). El `docker-compose.yml` monta este archivo como volumen, lo que sobrescribe la BD inicializada durante el build del contenedor. 

**Corrección aplicada:** Se ejecutó `python database_setup.py` dentro del contenedor en ejecución para inicializar las tablas sobre el archivo montado del host.

**Recomendación:** Eliminar la variable de volumen `./backend/tickets.db:/app/tickets.db` del `docker-compose.yml` y usar un volumen nombrado de Docker para persistencia.

---
*Evidencia generada durante la Auditoría de Sistemas – CORPORATE EPIS PILOT*
