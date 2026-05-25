# Reglas — Motor Python SysMho Venom

## Estado: ESTABILIZADO
El motor Python en `code/` está completo y funcional. Solo modificar si:
1. Hay un bug real confirmado
2. Se implementa Fase 2 del PLAN.md (bridge con PostgreSQL)
3. Se agrega un nuevo protocolo al sniffer

---

## Módulos y Responsabilidades (NO cambiar)

| Módulo | Responsabilidad | Puede tocar |
|--------|----------------|-------------|
| `venom_route.py` | Orquestación CLI | Solo Fase 2 (db_bridge call) |
| `arp_utils.py` | ARP spoofing/restauración | Solo bugs |
| `sniffer_engine.py` | Captura de tráfico | Solo Fase 2 (db_bridge call) |
| `iptables_utils.py` | Reglas iptables | Solo bugs |
| `network_utils.py` | Detección de red | Solo bugs |
| `anti_sniff_detector.py` | Detección de sniffers | Solo Fase 2 (db_bridge call) |
| `sniffer_utils.py` | Hashing SHA-256, filtros | Solo bugs |
| `ui_utils.py` | UI CLI, banners | Solo bugs |
| `db_bridge.py` | **NUEVO Fase 2** — BD persistence | Crear en Fase 2 |

---

## Reglas de Código

### Threading (patrón obligatorio)
```python
stop_event = threading.Event()
t = threading.Thread(target=funcion, args=(stop_event,), daemon=True)
t.start()
stop_event.set()
t.join(timeout=5)
```

### Cleanup (SIEMPRE en finally)
```python
try:
    # operación de red
finally:
    restore_arp()
    restaurar_iptables_forward()
    restaurar_masquerade_rule(interface)
    restaurar_forwarding()
```

### Subprocess (async siempre)
```python
proc = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
```
Nunca `subprocess.run()` bloqueante.

### db_bridge.py (Fase 2) — Patrón
```python
# db_bridge.py — única responsabilidad: persistencia
import psycopg2
import os

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "VENOM"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

def registrar_sesion(victim, gateway, iface, flags): ...
def registrar_artefacto(sesion_id, protocolo, ruta, sha256): ...
def registrar_deteccion(sesion_id, ip, mac, severidad): ...
def registrar_scan_hosts(sesion_id, hosts): ...
```

---

## Validación Antes de Commit

```bash
cd "/home/anderson/Documentos/programas personales/SysMho_Venom"
ruff check code/
python3 -m py_compile code/venom_route.py
python3 -m py_compile code/sniffer_engine.py
python3 -m py_compile code/arp_utils.py
```

---

## Prohibido

- `sudo python3 code/venom_route.py` desde Claude (requiere red real)
- `sudo iptables` desde Claude
- `subprocess.run(["sudo", ...])` sin confirmación explícita del usuario
- Cambiar la estructura de directorios de salida (`logs/`, `archivos_unicos/`, `sniff_detection/`) sin actualizar `DB.sql`
