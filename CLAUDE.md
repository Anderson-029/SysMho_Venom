# SysMho Venom — CLAUDE.md

## Qué es este proyecto

**Venom-Route** es una herramienta CLI de auditoría de redes para entornos autorizados. Motor Python puro: ARP spoofing, sniffing de tráfico clasificado por protocolo, detección pasiva de sniffers y gestión de iptables. Toda la evidencia se guarda como archivos locales (pcap/txt/sha256) — **sin base de datos ni dependencias externas de persistencia**.

Uso exclusivo en redes autorizadas. Requiere privilegios root.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Motor | Python 3.12 + Scapy + iptables |
| Persistencia | Archivos locales (pcap/txt/sha256) — sin BD |

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
│   ├── logs/                       # Evidencia capturada (pcap/txt por protocolo)
│   ├── archivos_unicos/            # Captura consolidada + hash global
│   └── AGENTS.md
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

**Nunca ejecutar `venom_route.py` ni comandos de red reales desde un agente** — requiere red autorizada real y privilegios root. Los agentes deben limitarse a análisis estático (`ruff check`, verificación de sintaxis, lectura de código).

---

## Evidencia Generada

Cada sesión genera sus propios archivos, automáticamente:
- `code/logs/<protocolo>/<PROTOCOLO>_<timestamp>.pcap` + `.txt` — captura por protocolo.
- `code/archivos_unicos/captura_total_<timestamp>.pcap` — captura consolidada.
- `code/archivos_unicos/hash_captura_global.txt` — SHA-256 del pcap global.
- `code/sniff_detection/log.txt` — hallazgos del detector anti-sniffer.

Esto es el comportamiento esperado del motor, no algo que limpiar entre ejecuciones (salvo que se quiera liberar espacio manualmente).

---

## Convenciones de Código

- Módulos en `code/` con responsabilidad única (ver tabla arriba).
- Cleanup obligatorio en `finally` (restaurar ARP e iptables) al finalizar o ante error.
- `check_root()` al inicio de cualquier operación que requiera privilegios.
- Threads con `threading.Event` como señal de parada (ver `code/AGENTS.md`).
- Subprocesos siempre async (`asyncio.create_subprocess_exec`), nunca `subprocess.run` bloqueante.
- Cada evidencia capturada (pcap/txt) lleva su `.sha256` correspondiente.
- `ruff check code/` debe pasar sin errores antes de cualquier commit.

---

## Seguridad Operacional

- **Nunca ejecutar en redes no autorizadas.**
- El motor requiere root — limitar acceso al binario/script.

---

## Estado Actual del Proyecto

Proyecto reducido a su núcleo original: el motor CLI en `code/`, sin ninguna capa web ni de base de datos. Toda persistencia es vía archivos locales.
