# Reglas — Motor Python SysMho Venom

## Estado: ESTABILIZADO
El motor Python en `code/` está completo y funcional, 100% basado en archivos locales (sin BD). Solo modificar si:
1. Hay un bug real confirmado
2. Se agrega un nuevo protocolo al sniffer

---

## Módulos y Responsabilidades (NO cambiar)

| Módulo | Responsabilidad | Puede tocar |
|--------|----------------|-------------|
| `venom_route.py` | Orquestación CLI | Solo bugs |
| `arp_utils.py` | ARP spoofing/restauración | Solo bugs |
| `sniffer_engine.py` | Captura de tráfico | Solo bugs |
| `iptables_utils.py` | Reglas iptables | Solo bugs |
| `network_utils.py` | Detección de red | Solo bugs |
| `anti_sniff_detector.py` | Detección de sniffers | Solo bugs |
| `sniffer_utils.py` | Hashing SHA-256, filtros | Solo bugs |
| `ui_utils.py` | UI CLI, banners | Solo bugs |

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
- Cambiar la estructura de directorios de salida (`logs/`, `archivos_unicos/`, `sniff_detection/`) sin avisar al usuario — otras herramientas o scripts pueden depender de esas rutas
