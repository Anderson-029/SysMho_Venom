# AGENTS.md — code/ (Motor Python de Red)

## Responsabilidad

Este directorio contiene el motor de auditoría de red. Cada módulo tiene responsabilidad única y se coordina a través de `venom_route.py`. Toda la evidencia se persiste como archivos locales — sin base de datos.

---

## Módulos y su Función

| Archivo | Responsabilidad |
|---------|----------------|
| `venom_route.py` | Entry point CLI — orquesta todos los módulos |
| `sniffer_engine.py` | Captura tráfico, clasifica por protocolo, guarda pcap + txt |
| `arp_utils.py` | ARP spoofing victim↔gateway, restauración limpia |
| `iptables_utils.py` | Habilitar/restaurar IP forwarding y MASQUERADE |
| `network_utils.py` | Detección de interfaces, CIDR, escaneo ARP de red |
| `anti_sniff_detector.py` | Detecta hosts en modo promiscuo enviando ARP falsos |
| `sniffer_utils.py` | Hash SHA-256 de evidencias, filtro de dominios DNS |
| `ui_utils.py` | Colores terminal, banner ASCII, spinners, check_root() |
| `venom_logger.py` | Log de funcionamiento interno del motor (`logs/venom_engine.log`) |
| `limpiar_logs.py` | Utilidad de mantenimiento: borra evidencia sin tocar la estructura de carpetas |

---

## Reglas para Agentes que Modifiquen este Directorio

### Seguridad (OBLIGATORIO)
- **Nunca ejecutar** `venom_route.py` ni comandos de red reales — solo análisis estático.
- Toda función que lance subprocesos o threads debe tener `stop_event` como `threading.Event`.
- Cleanup de ARP e iptables SIEMPRE en bloque `finally`, no solo en happy path.
- `check_root()` debe llamarse antes de cualquier operación que requiera privilegios.

### Manejo de Threads
```python
stop_event = threading.Event()
t = threading.Thread(target=funcion, args=(stop_event,), daemon=True)
t.start()
# ...
stop_event.set()
t.join(timeout=5)
```

### Integridad de Evidencias
- Cada archivo pcap o txt capturado debe tener un `.sha256` correspondiente.
- Usar `sniffer_utils.generar_hash_sha256()` — no reimplementar hashing.
- Directorio de salida: `logs/<PROTOCOLO>/` y `archivos_unicos/` — no cambiar la estructura sin avisar al usuario, otros scripts pueden depender de estas rutas.

### Restauración de Red
Al finalizar (Ctrl+C o error), siempre llamar en orden:
1. `restore_arp()` para victim y gateway.
2. `restaurar_iptables_forward()` si se activó.
3. `restaurar_masquerade_rule()` si se activó.
4. `restaurar_forwarding()` al final.

---

## Validación Antes de Commit

```bash
cd /ruta/proyecto
ruff check code/
python3 -m py_compile code/venom_route.py
python3 -m py_compile code/sniffer_engine.py
```
