# SysMho Venom — CLAUDE.md

## Qué es este proyecto

**Venom-Route** es una herramienta CLI de auditoría de redes para entornos autorizados. Motor Python puro: ARP spoofing, sniffing de tráfico clasificado por protocolo, detección pasiva de sniffers y gestión de iptables, con persistencia opcional en PostgreSQL.

Uso exclusivo en redes autorizadas. Requiere privilegios root.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Motor | Python 3.12 + Scapy + iptables |
| Persistencia (opcional) | PostgreSQL vía `psycopg2` |

---

## Estructura del Proyecto

```
SysMho_Venom/
├── code/                        # Motor Python — único componente ejecutable
│   ├── venom_route.py              # Entry point CLI
│   ├── sniffer_engine.py           # Captura y clasificación de tráfico
│   ├── arp_utils.py                # ARP spoofing y restauración
│   ├── iptables_utils.py           # Gestión de reglas iptables
│   ├── network_utils.py            # Detección de interfaces, escaneo ARP
│   ├── anti_sniff_detector.py      # Detección pasiva de sniffers
│   ├── sniffer_utils.py            # Hashing SHA-256, filtro DNS
│   ├── ui_utils.py                 # Colores terminal, banner, spinners, check_root()
│   ├── db_bridge.py                # Bridge opcional Python ↔ PostgreSQL (psycopg2)
│   ├── logs/                       # Evidencia capturada (pcap/txt por protocolo)
│   ├── archivos_unicos/            # Captura consolidada + hash global
│   └── AGENTS.md
├── SQL/                         # Schema PostgreSQL (solo si se usa persistencia)
│   ├── DB.sql
│   ├── funcion_auditoria_y_triggers.sql
│   └── AGENTS.md
├── .env                         # Credenciales de BD (no versionar valores reales)
└── .claude/                     # Configuración Claude Code
```

---

## Cómo Ejecutar el Motor

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

**Nunca ejecutar `venom_route.py` ni comandos de red reales desde un agente** — requiere red autorizada real y privilegios root. Los agentes deben limitarse a análisis estático (`ruff check`, `py_compile`, lectura de código).

---

## Base de Datos (opcional)

Si se usa persistencia, el schema vive en `SQL/DB.sql` (12 tablas) + triggers de auditoría en `SQL/funcion_auditoria_y_triggers.sql`. Conexión configurada vía `.env`:

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=venom
DB_USER=postgres
DB_PASS=...
```

`db_bridge.py` debe fallar silenciosamente (o con advertencia simple) si la BD no está disponible — el CLI nunca debe depender de la base de datos para funcionar.

---

## Convenciones de Código

- Módulos en `code/` con responsabilidad única (ver tabla arriba).
- Persistencia vía `db_bridge.py` usando `psycopg2`, opcional y no bloqueante.
- Cleanup obligatorio en `finally` (restaurar ARP e iptables) al finalizar o ante error.
- `check_root()` al inicio de cualquier operación que requiera privilegios.
- Threads con `threading.Event` como señal de parada (ver `code/AGENTS.md`).
- Subprocesos siempre async (`asyncio.create_subprocess_exec`), nunca `subprocess.run` bloqueante.
- Cada evidencia capturada (pcap/txt) lleva su `.sha256` correspondiente.
- `ruff check code/` debe pasar sin errores antes de cualquier commit.

---

## Seguridad Operacional

- **Nunca ejecutar en redes no autorizadas.**
- Credenciales de BD nunca en texto plano en el código — siempre vía `.env` / `os.getenv()`.
- El motor requiere root — limitar acceso al binario/script.

---

## Estado Actual del Proyecto

Proyecto reducido a su núcleo original: el motor CLI en `code/`. Toda la capa web (backend PHP, API REST, admin panel, landing) que se exploró en una sesión anterior fue eliminada — este repositorio es de nuevo exclusivamente la herramienta de línea de comandos.
