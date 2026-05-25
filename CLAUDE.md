# SysMho Venom — CLAUDE.md

## Qué es este proyecto

**Venom-Route** es una herramienta de auditoría de redes para entornos autorizados. Combina:

- **Motor Python** (ARP spoofing, sniffing de tráfico, detección de sniffers, iptables)
- **Backend PHP + PostgreSQL** (autenticación de administrador, sesiones, evidencias)
- **API REST en PHP** (bajo la carpeta `/api/`) para conectar el frontend con la base de datos y el motor
- **Frontend unificado** (Admin Panel en `admin-panel/`) con JavaScript vanilla
- **Landing page** de marketing con formulario de contacto

Uso exclusivo en redes autorizadas. MITM y captura de tráfico requieren privilegios root.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Motor de red | Python 3.12 + Scapy + iptables |
| Backend web | PHP 8+ + PostgreSQL |
| API REST | PHP nativo (en `/api/`) |
| Frontend | HTML5 + CSS3 + JavaScript vanilla |
| Base de datos | PostgreSQL (schema en `SQL/DB.sql` + triggers de auditoría) |

---

## Estructura del Proyecto

```
SysMho_Venom/
├── code/               # Motor Python (MITM, sniffer, ARP, iptables)
│   ├── venom_route.py      # Entry point CLI
│   ├── sniffer_engine.py   # Captura y clasificación de tráfico
│   ├── arp_utils.py        # ARP spoofing y restauración
│   ├── iptables_utils.py   # Gestión de reglas iptables
│   ├── network_utils.py    # Detección de interfaces, escaneo ARP
│   ├── anti_sniff_detector.py  # Detección pasiva de sniffers
│   ├── sniffer_utils.py    # Hashing SHA-256, filtro DNS
│   ├── ui_utils.py         # Colores terminal, banner, spinners
│   └── db_bridge.py        # Bridge Python ↔ PostgreSQL (psycopg2)
├── api/                # API REST en PHP (despachada por router index.php)
│   ├── index.php           # Enrutador principal
│   ├── middleware.php      # Verificación de sesión y cabeceras JSON
│   ├── sessions.php        # Endpoint de gestión de sesiones
│   ├── logs.php            # Endpoint de listado y descarga de evidencias
│   ├── users.php           # Endpoint para gestión de usuarios
│   ├── antisniffer.php     # Endpoint de detecciones anti-sniffer
│   ├── audit.php           # Endpoint para el trail de auditoría
│   ├── stats.php           # Endpoint de estadísticas agregadas (KPIs)
│   ├── reports.php         # Endpoint para exportar reportes
│   ├── network.php         # Endpoint para interactuar con la red
│   ├── arp.php             # Endpoint para inicio/restauración de ARP
│   └── sniffer.php         # Endpoint para iniciar/detener sniffer
├── backend/            # PHP: autenticación y sesiones
│   ├── config.php          # Conexión PostgreSQL (usa variables de entorno)
│   ├── auth.php            # Middleware de sesión (únicamente admin)
│   ├── login.php           # Procesador de login (prepared statements)
│   └── logout.php          # Destructor de sesión
├── admin-panel/        # Dashboard Unificado (con controles según privilegios)
│   ├── admin.php           # HTML principal
│   ├── admin.js            # Lógica SPA y llamadas a la API REST (USE_MOCK disponible)
│   └── admin.css           # Estilos dark theme
├── SQL/                # Schema y triggers PostgreSQL
│   ├── DB.sql              # Estructura de tablas y catálogos iniciales
│   └── funcion_auditoria_y_triggers.sql # Triggers BEFORE UPDATE de auditoría
├── landing/            # Página de marketing
└── .claude/            # Configuración Claude Code
```

---

## Roles de Usuario

El sistema ha sido simplificado a un diseño de **Administrador Único (Single Admin)** para mantener coherencia y estabilidad:

| Rol | Permisos |
|-----|---------|
| `admin` | Único rol permitido (`CHECK (rol IN ('admin'))`). Control total de la plataforma. |

---

## Cómo Ejecutar el Motor Python

```bash
# Requiere root
sudo python3 code/venom_route.py -v VICTIM_IP -g GATEWAY_IP -i INTERFACE

# Modo interactivo (detecta red automáticamente)
sudo python3 code/venom_route.py -I

# Con opciones avanzadas
sudo python3 code/venom_route.py -v 192.168.1.10 -g 192.168.1.1 -i eth0 -F -M -A
# -F: activar IP FORWARD
# -M: activar MASQUERADE (NAT)
# -A: activar anti-sniffer detector
```

---

## Base de Datos

Schema completo en `SQL/DB.sql` con **12 tablas principales:**

| Tabla | Descripción |
|-------|------------|
| `tab_Usuarios` | Cuentas de admin, autenticación con bcrypt |
| `tab_Alcances` | Scopes autorizados (redes a monitorear) |
| `tab_Runners` | Agentes que ejecutan el motor Python |
| `tab_Sesiones` | Sesiones MITM (ARP spoofing activo) |
| `tab_Artefactos` | Evidencias capturadas (PCAP, logs, hashes SHA-256) |
| `tab_Detecciones` | Hallazgos del detector anti-sniffer |
| `tab_Eventos_sesion` | Auditoría de eventos por sesión |
| `tab_Protocolos` | Catálogo de protocolos monitoreados |
| `tab_Tipo_evidencia` | Tipos de evidencia (PCAP, DNS, HASH, etc.) |
| `tab_Stats_protocolo` | Estadísticas por protocolo y sesión |
| `tab_Scan_hosts` | Hosts descubiertos en la red |
| `tokens_invitacion` | Tokens para invitar nuevos admins |

**Configuración de conexión:** Variables de entorno en `.env`:
```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=venom       # ⚠️ Minúsculas (PostgreSQL lo convierte automáticamente)
DB_USER=postgres
DB_PASS=ander123
```

**Auto-carga en PHP:** `backend/config.php` lee `.env` automáticamente si las variables de entorno no están disponibles.

---

## Flujo Principal

```
1. CLI (Motor Python) ↔ db_bridge.py ↔ PostgreSQL
   ├─ network_utils.py → detectar interfaz y red
   ├─ arp_utils.py → ARP spoofing victim ↔ gateway
   ├─ iptables_utils.py → habilitar forwarding/masquerade
   ├─ sniffer_engine.py → capturar y clasificar tráfico
   └─ anti_sniff_detector.py → detectar sniffers pasivos

2. API REST (/api/) ↔ PostgreSQL
   ├─ Recibe peticiones desde el frontend (admin.js)
   ├─ Realiza operaciones sobre la BD con prepared statements

3. Frontend (admin-panel/) ↔ /api/
   └─ Dashboard SPA para visualizar KPIs, controlar operaciones y descargar evidencias
```

---

## Convenciones de Código

### Python
- Módulos en `code/` con responsabilidad única.
- Persistencia vía `db_bridge.py` usando `psycopg2`. Falla de forma silenciosa si la BD no está disponible.
- Cleanup obligatorio en `finally` (restaurar ARP e iptables).
- `check_root()` al inicio de cualquier operación que requiera privilegios.

### PHP
- `auth.php` verifica sesión activa y rol `admin`. Redirige a landing si no hay sesión.
- Prepared statements (`pg_prepare`/`pg_execute`) usados para evitar inyección SQL.
- `config.php` carga automáticamente `.env` con `parse_ini_file()` y establece variables con `putenv()`.
- Login: `backend/login.php` valida credenciales contra `tab_usuarios`, hashea con bcrypt.
- Sesiones PHP: `PHPSESSID` cookie establece variables: `user_id`, `user_name`, `user_role`, `user_email`.
- Bridge login: `landing/login.php` redirige a `backend/login.php` (mismo script).

### JavaScript
- **Landing page** (`landing/`): Vanilla JS sin frameworks, modales de login/signup
  - Login form POST a `/landing/login.php` con email y password
  - Sigue redirects HTTP 302 al dashboard admin
  - Valida email y contraseña antes de enviar
- **Admin panel** (`admin-panel/`): SPA con navegación por `data-view`
  - Llamadas fetch a `/api/` requieren sesión autenticada (PHPSESSID cookie)
  - Mock endpoints disponibles en `admin.js` (flag `USE_MOCK` para desarrollo)

---

## Seguridad Operacional

- **Nunca ejecutar en redes no autorizadas.**
- Las credenciales de BD no deben subirse en texto plano; se cargan mediante entorno.
- El motor Python requiere root — limitar acceso al binario.

---

## Estado Actual del Proyecto (24 May 2026)

### ✅ Completado
- Sistema funcional con PHP server en `localhost:8000`
- PostgreSQL inicializado con 12 tablas + triggers de auditoría
- Usuario admin creado (`admin@venom.local` / `admin123`)
- Landing page accesible con modal de login
- Flujo de autenticación completo (landing → login → dashboard)
- API REST configurada en `/api/` (router + middleware + endpoints)
- Backend de configuración auto-carga `.env`
- Dashboard admin completamente funcional

### ⏳ En Progreso
- **Pruebas manuales de interfaz**: Explorar todos los controles del dashboard
- **Integración CLI ↔ BD**: Conectar motor Python con la base de datos
- **Inyección de datos de prueba**: Poblar BD para visualizar en dashboard

### 📋 Pendientes
- Motor Python (`code/venom_route.py`) no probado en red real aún
- Endpoints de CRUD en `/api/` sin datos reales
- Formulario de demo en landing page (no implementado aún)
- Reportes exportables en formato PDF/HTML
