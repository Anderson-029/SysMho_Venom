# AGENTS.md — SysMho Venom (Raíz)

## Propósito del Proyecto

Venom-Route es una plataforma de auditoría de redes compuesta por:
1. **Motor Python** — ejecuta MITM, captura tráfico, detecta sniffers y persiste en BD usando `db_bridge.py`
2. **API REST PHP** — proporciona los endpoints de comunicación con la base de datos
3. **Backend PHP** — maneja autenticación y sesiones de administrador
4. **Frontend unificado** — Admin Panel que consume los datos de la API REST
5. **Base de datos PostgreSQL** — persistencia completa con triggers de auditoría

---

## Agentes Disponibles

### `network-engine-agent`
**Carpeta:** `code/`
**Rol:** Desarrollo y mantenimiento del motor Python de red
- Modifica módulos de ARP spoofing, sniffing, iptables, detección y persistencia a PostgreSQL (`db_bridge.py`)
- Ejecuta análisis estático de código Python
- **NO ejecutar** `venom_route.py` directamente — requiere root y red real

### `api-agent`
**Carpeta:** `api/`
**Rol:** Desarrollo y mantenimiento de la API REST en PHP
- Modifica enrutadores, middleware de cabeceras JSON, y endpoints (`sessions.php`, `logs.php`, `stats.php`, etc.)
- Valida que todos los endpoints devuelvan respuestas JSON correctas y controlen errores HTTP apropiados

### `backend-agent`
**Carpeta:** `backend/`
**Rol:** Autenticación PHP y gestión de sesiones de administrador
- Modifica `config.php`, `auth.php`, `login.php`, `logout.php`
- Valida flujos de autenticación únicamente para el rol `admin`
- Verifica que no se filtren credenciales en logs ni respuestas HTTP

### `frontend-admin-agent`
**Carpeta:** `admin-panel/`
**Rol:** Dashboard unificado del administrador
- Modifica `admin.php`, `admin.js`, `admin.css`
- Conecta endpoints mock con la API PHP real
- Mantiene la consistencia visual y de comportamiento SPA de la plataforma

### `database-agent`
**Carpeta:** `SQL/`
**Rol:** Schema PostgreSQL, triggers y funciones de auditoría
- Modifica `DB.sql` y `funcion_auditoria_y_triggers.sql`
- Valida e implementa triggers de actualización automática y la integridad referencial de las tablas

### `landing-agent`
**Carpeta:** `landing/`
**Rol:** Página de marketing
- Modifica `index.html`, `script.js`, `style.css`
- Conecta el formulario de login al backend PHP
- No modificar imágenes ni videos

---

## Reglas Globales para Todos los Agentes

### Seguridad Operacional (CRÍTICO)
- **Nunca generar** comandos que ejecuten el motor MITM contra IPs reales
- **Nunca hardcodear** credenciales de BD — siempre cargarlas con `getenv()`
- Los payloads y operaciones de red son **solo para redes autorizadas**
- Cualquier cambio en `arp_utils.py` o `iptables_utils.py` debe mantener el cleanup en `finally`

### Calidad de Código
- Python: pasar `ruff check code/` sin errores
- PHP: validar sintaxis con `php -l archivo.php`
- JavaScript: no introducir `eval()`, `innerHTML` con datos de usuario sin sanitizar
- SQL: nuevas tablas deben incluir columnas de auditoría (`usr_insert`, `fec_insert`, etc.) y mantener la restricción del rol único (`admin`)

### Integridad de Evidencias
- Los artefactos capturados siempre tienen hash SHA-256 asociado
- No modificar el formato de directorio de salida del sniffer sin actualizar el schema

### Roles y Acceso
- El sistema utiliza una arquitectura de **Administrador Único (Single Admin)**.
- Toda página PHP nueva debe incluir `require_once '../backend/auth.php'` al inicio para denegar el acceso a sesiones no autorizadas.

---

## Contexto de Desarrollo

- **Lenguaje principal backend/API:** PHP 8+
- **Motor de red:** Python 3.12 con Scapy y `psycopg2`
- **BD:** PostgreSQL — schema en `SQL/DB.sql` y triggers en `SQL/funcion_auditoria_y_triggers.sql`
- **Frontend:** JavaScript vanilla (sin React, sin frameworks)
- **Estilos:** CSS custom properties, dark theme por defecto

### Puertos Estándar
| Servicio | Puerto |
|----------|--------|
| Apache/Nginx (paneles) | 80 / 443 |
| PostgreSQL | 5432 |

### Comandos de Validación
```bash
# Python
ruff check code/

# PHP
php -l backend/auth.php
php -l admin-panel/admin.php
php -l api/index.php

# SQL (conectado a postgres)
psql -U postgres -d venom -f SQL/DB.sql --dry-run
```
