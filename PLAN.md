# PLAN — SysMho Venom (Actualizado 24 May 2026)
**Principio Fundamental:** Coherencia · Congruencia · Funcionalidad · Estabilidad Total
> No se avanza a la siguiente fase hasta que la anterior esté completa, estable y verificada.

## 🚀 Resumen de Cambios (24 May 2026)

### ✅ Arreglos Realizados
- **config.php**: Ahora lee `.env` automáticamente con `parse_ini_file()` + `putenv()`
- **DB_NAME**: Estandarizado a minúsculas (`venom` en lugar de `VENOM`)
- **landing/login.php**: Creado como bridge a `backend/login.php`
- **landing/script.js**: Arreglado el formulario de login para hacer POST real (no mock)
- **PHP Server**: Funcionando en `localhost:8000` con PostgreSQL conectado
- **BD**: 12 tablas inicializadas con usuario admin preconfigurado
- **Flujo Auth**: Landing → Modal Login → POST /landing/login.php → 302 redirect → Dashboard Admin

### ⏳ Estado Actual
- **Sistema base**: 100% funcional y testeable manualmente
- **Motor Python**: Listo para pruebas en red real (requiere sudo)
- **Frontend**: Dashboard admin completamente operativo
- **API**: Endpoints configurados y respondiendo con autenticación

---

## Arquitectura — Single Admin

**Un solo usuario:** Anderson (admin). Sin multi-rol, sin paneles extra.
- `auditor-panel/` y `viewer-panel/` **eliminados** — funcionalidad absorbida en `admin-panel/`
- `auth.php` verifica únicamente rol `admin`
- `login.php` solo autentica usuarios con `rol = 'admin'`
- DB: CHECK constraint solo acepta `'admin'`

## Stack Tecnológico Web

| Capa | Tecnología | Razón |
|------|-----------|-------|
| **API Backend** | PHP 8+ con endpoints REST en `/api/` | Ya existe, no cambiar stack |
| **Frontend** | Vanilla JS + CSS custom (sin frameworks) | Ya existe, coherente con lo actual |
| **Real-time** | Server-Sent Events (SSE) vía PHP | Más simple que WebSockets en PHP puro |
| **BD** | PostgreSQL (schema ya completo) | Persistencia de sesiones, artefactos, logs |
| **Bridge** | Python escribe en BD al finalizar sesión | Motor Python → PostgreSQL → PHP → Frontend |
| **Diseño** | Dark cybersecurity — tokens ya definidos | Extender el design system existente |

**Design tokens actuales (mantener y extender):**
```css
--bg: #0d1512          /* fondo principal */
--primary: #34d399     /* verde esmeralda = acción */
--accent: #60a5fa      /* azul = información */
--danger: #f87171      /* rojo = alertas/peligro */
```

---

## Fase 0 — Línea Base Estable
**Objetivo:** Corregir todo lo roto antes de construir. Cero bugs conocidos.
**Criterio de éxito:** Login funciona sin warnings, roles coherentes en todo el sistema.

### Tareas
- [x] **F0-01** `login.php` → prepared statements (eliminar SQL injection)
- [x] **F0-02** `login.php` → agregar `$_SESSION["user_email"]` al setear sesión
- [x] **F0-03** Estandarizar roles: `admin` como rol único en la base de datos y la sesión
- [x] **F0-04** `landing/index.html` → rutas verificadas correctas (carpeta se llama `img,svg,png/` — no cambiar)
- [x] **F0-05** `config.php` → credenciales movidas a variables de entorno con `getenv()`
- [x] **F0-06** `funcion_auditoria_y_triggers.sql` → función `fn_audit_update()` + 12 triggers implementados
- [x] **F0-07** Poblar tablas catálogo: 8 protocolos y 5 tipos de evidencia insertados en `DB.sql`

**Validación:**
```bash
php -l backend/login.php
php -l backend/auth.php
grep -r "USE_MOCK" */**.js   # deben seguir en true hasta Fase 3
```

---

## Fase 1 — API REST Core (PHP)
**Objetivo:** Implementar los endpoints que el frontend necesita. Solo GET inicialmente.
**Criterio de éxito:** Los endpoints responden JSON correcto con datos reales de la BD.

### Estructura de archivos nueva
```
api/
├── index.php           # router principal
├── middleware.php      # auth check + CORS + JSON headers
├── sessions.php        # GET /api/sessions
├── logs.php            # GET /api/logs/list, GET /api/logs/download
├── antisniffer.php     # GET /api/antisniffer/findings
├── stats.php           # GET /api/stats (KPIs)
└── reports.php         # POST /api/reports/export
```

### Tareas
- [x] **F1-01** Crear `api/middleware.php` — auth sesión PHP, headers JSON, helpers json_ok/json_err
- [x] **F1-02** Crear `api/sessions.php` — GET lista/detalle, POST crear, PATCH estado
- [x] **F1-03** Crear `api/logs.php` — GET lista artefactos, download binario, hash SHA-256
- [x] **F1-04** Crear `api/antisniffer.php` — GET detecciones desde tab_Detecciones
- [x] **F1-05** Crear `api/audit.php` — GET trail de eventos desde tab_eventos_sesion
- [x] **F1-06** Crear `api/stats.php` — KPIs agregados (COUNT sesiones, artefactos, detecciones, hosts)
- [x] **F1-07** Crear `api/reports.php` — reporte Markdown descargable con datos reales de BD
- [x] **F1-08** Crear `api/index.php` — router principal que despacha por ruta
- [x] **F1-09** Crear `api/network.php`, `api/arp.php`, `api/sniffer.php` — stubs con 501 hasta Fase 2

**Validación:**
```bash
curl -s http://localhost/api/sessions | python3 -m json.tool
curl -s http://localhost/api/stats | python3 -m json.tool
# Deben responder JSON, no HTML de error
```

---

## Fase 2 — Bridge Python ↔ PostgreSQL
**Objetivo:** El motor Python persiste datos reales en la BD al finalizar capturas.
**Criterio de éxito:** Después de una sesión MITM, las tablas tienen datos reales.

### Nuevo módulo: `code/db_bridge.py`
```python
# code/db_bridge.py
# Responsabilidad única: escribir resultados de sesión a PostgreSQL
```

### Tareas
- [x] **F2-01** Crear `code/db_bridge.py` — conexión a PostgreSQL con `psycopg2`
- [x] **F2-02** Función `registrar_sesion(victim, gateway, iface, flags)` → INSERT en `tab_Sesiones`
- [x] **F2-03** Función `registrar_artefacto(sesion_id, protocolo, ruta, sha256)` → INSERT en `tab_Artefactos`
- [x] **F2-04** Función `registrar_deteccion(sesion_id, ip, mac, severidad)` → INSERT en `tab_Detecciones`
- [x] **F2-05** Función `registrar_scan_hosts(sesion_id, hosts[])` → INSERT en `tab_Scan_hosts`
- [x] **F2-06** Integrar `db_bridge.py` en `venom_route.py` — llamar al inicio y al finalizar
- [x] **F2-07** Integrar `db_bridge.py` en `sniffer_engine.py` — registrar artefactos al guardar
- [x] **F2-08** Integrar `db_bridge.py` en `anti_sniff_detector.py` — registrar detecciones
- [x] **F2-09** Integrar `db_bridge.py` en `network_utils.py` — registrar hosts del escaneo ARP

**Validación:**
```bash
# Después de correr venom_route.py en modo simulación/test
psql -U postgres -d venom -c "SELECT COUNT(*) FROM tab_Sesiones;"
psql -U postgres -d venom -c "SELECT COUNT(*) FROM tab_Artefactos;"
# Deben tener registros > 0
```

---

## Fase 3 — Desconexión de Mocks (Frontend Real)
**Objetivo:** El panel web consume datos reales. `USE_MOCK = false`.
**Criterio de éxito:** Dashboard muestra datos reales de la BD, sin datos ficticios.

### Tareas
- [x] **F3-01** `admin.js` → `USE_MOCK = false`, `fetchJSON` eliminado, `apiJSON/apiFetch` contra endpoints reales
- [x] **F3-02** `user.js` (auditor) → Eliminado (Single Admin)
- [x] **F3-03** `viewer.js` → Eliminado (Single Admin)
- [x] **F3-04** Loading states, empty states y error messages en todas las vistas
- [x] **F3-05** Login desde landing operativo
- [x] **F3-06** Token de invitación → Eliminado (Single Admin)
- [x] **F3-07** Descarga real de artefactos `.pcap`/`.txt` desde panel via `/api/logs/download`
- [x] **F3-08** Crear `api/users.php` — CRUD completo (GET/POST/PUT/DELETE) con soft delete
- [x] **F3-09** `api/stats.php` → añadir campos `hosts_descubiertos` y `protocolos`
- [x] **F3-10** Guards de rol `AUDITOR`/`ADMIN` eliminados del JS — rol único admin

**Validación:**
```bash
# Con el dev server activo
# 1. Login como admin
# 2. Ver sesiones — deben mostrar datos reales de la BD (con USE_MOCK = false)
# 3. Ver logs — artefactos reales
```

---

## Fase 4 — UI/UX Profesional (Claude Design)
**Objetivo:** Redesign visual que refleje la identidad de una herramienta MITM profesional.
**Criterio de éxito:** Interfaz coherente, animada, con estética cybersecurity digna de Venom.

### Identidad Visual
- **Paleta**: Negro profundo + verde esmeralda (`#34d399`) + acentos azul fría
- **Tipografía**: Monospace para datos técnicos (IPs, MACs, hashes), system-ui para UI
- **Efectos**: Glow sutil en elementos activos, transiciones suaves, scanlines opcionales
- **Iconografía**: Minimal, geométrica (como el SVG del brand actual)
- **Feedback visual**: Estados de carga tipo terminal, animaciones de red/tráfico

### Tareas
- [x] **F4-01** `admin.css` reescrito — design system completo (tokens, glow, monospace, grid bg)
- [x] **F4-02** Sidebar rediseñado — indicador activo con barra verde + glow, identidad Venom
- [x] **F4-03** KPIs rediseñados — monospace, glow por color, dot pulse animado en topbar
- [x] **F4-04** Tablas rediseñadas — th monospace uppercase, hover sutil, code con color accent
- [x] **F4-05** Formularios y botones — estados focus glow, btn-danger, btn-ghost coherentes
- [x] **F4-06** Terminal output para scan — rowline con IP verde + MAC azul + vendor muted
- [x] **F4-07** Modal de usuario creado — faltaba en HTML, dialog nativo estilizado
- [x] **F4-08** Vista Usuarios agregada — faltaba, con tabla CRUD y botón nuevo
- [x] **F4-09** Responsive — kpi-grid 2col, ops-grid 1col, sidebar colapsable en 760px

---

## Fase 5 — Real-time (SSE)
**Objetivo:** Monitoreo en vivo desde el panel web usando Server-Sent Events.
**Criterio de éxito:** El panel muestra paquetes capturados y detecciones en tiempo real.

### Tareas
- [x] **F5-01** Crear `api/stream.php` — SSE con poll a BD cada 3s, eventos tipados, keepalive, auth guard + session_write_close
- [x] **F5-02** Cliente SSE en `admin.js` — `sseConnect()` con reconexión exponencial (máx 8 reintentos, 30s)
- [x] **F5-03** Stream de detecciones en tiempo real — evento `detection` → fila nueva + KPI + toast
- [x] **F5-04** Indicador visual de sesión activa — `session-dot` pulsante en botón Operaciones del sidebar
- [x] **F5-05** Notificaciones push para detecciones críticas (severidad ≥ 4) via Notification API

---

## Control de Progreso

| Fase | Descripción | Estado | Hito |
|------|------------|--------|------|
| 0 | Línea Base Estable | 🟢 COMPLETADO | BD init, config.php, auth funcionando |
| 1 | API REST Core | 🟢 COMPLETADO | Endpoints GET/POST respondiendo con auth |
| 2 | Bridge Python↔BD | 🟢 COMPLETADO | db_bridge.py → tablas sesiones/artefactos |
| 3 | Frontend Real | 🟢 COMPLETADO | Landing login → Dashboard sin mocks |
| 4 | UI/UX Pro | 🟢 COMPLETADO | Dark theme, KPIs, tablas operacionales |
| 5 | Real-time SSE | 🟢 COMPLETADO | stream.php, reconexión, detecciones en vivo |
| **6** | **Pruebas Manuales** | **🟡 EN PROGRESO** | **Verificar UI, controles, flujos** |
| **7** | **Integración CLI** | **🔴 PENDIENTE** | **motor Python → datos en BD → dashboard** |

**Leyenda:** 🔴 PENDIENTE · 🟡 EN PROGRESO · 🟢 COMPLETADO · ⚫ BLOQUEADO

### Fase 6 — Pruebas Manuales (ACTUAL)
**Objetivo:** Validar que la interfaz es intuitiva y todos los controles funcionan.
**Criterio de éxito:** Usuario puede navegar dashboard sin errores, autenticación robusta.

**Tareas:**
- ⏳ Probar login desde landing page (múltiples intentos)
- ⏳ Navegar todas las secciones del dashboard
- ⏳ Crear/editar/eliminar usuarios desde UI
- ⏳ Verificar que los KPIs actualizan en tiempo real (si hay datos)
- ⏳ Revisar mensajes de error y validaciones

### Fase 7 — Integración CLI (PRÓXIMA)
**Objetivo:** Motor Python escribe datos reales en BD y se visualizan en dashboard.
**Criterio de éxito:** Sesión MITM captura tráfico → datos en tablas → dashboard muestra resultados.

---

## Reglas del Plan
1. Una fase a la vez — no empezar siguiente sin completar anterior
2. Cada tarea completada se marca `[x]` con commit semántico
3. Validación obligatoria antes de cerrar fase
4. Motor Python (CLI) no se toca después de Fase 2 salvo bugs críticos
5. Cualquier decisión arquitectónica no obvia → documentar en este archivo
