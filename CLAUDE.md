# SysMho Venom — CLAUDE.md

## Consigna Principal — 4 Pilares Obligatorios

Antes de dar por terminado cualquier cambio en este proyecto, confirmar explícitamente:

1. **Coherencia** — el código nuevo sigue el mismo estilo, patrones y estructura que el resto de módulos (ver `.claude/rules/venom_python.md`), no inventa formas nuevas de resolver algo que ya tiene una convención establecida.
2. **Congruencia** — el cambio está alineado con la documentación (`CLAUDE.md`, `MANUAL.md`, `AGENTS.md`) y con el comportamiento real del resto de la herramienta; si algo cambia, la documentación se actualiza junto con el código.
3. **Estabilidad** — no se rompe el flujo existente (ataque, sniffer, cleanup, restauración); se valida sintaxis y, cuando sea posible, se ejecuta `ruff check` antes de considerar el cambio terminado.
4. **Funcionalidad** — el cambio hace exactamente lo que se pidió, ni más ni menos, y de verdad resuelve el problema (no una aproximación a medias).

Esto aplica a todo cambio, sin excepción, y debe confirmarse activamente antes de reportar una tarea como completada.

---

## Regla de Oro — El Código es la Fuente de Verdad

**Antes de hacer cualquier afirmación sobre cómo funciona el código, verifica el código fuente directamente.** No des respuestas basadas en suposiciones, memoria, o interpretaciones aproximadas.

Aplicado a desarrollo:
- ¿"¿Dónde se guardan los hashes?"** → Lee `sniffer_engine.py` línea por línea. Verifica exactamente qué se ejecuta.
- ¿"¿El hash se genera para el .pcap o el .txt?"** → Abre el código, no asumas.
- ¿"¿Qué hace esta función cuando falla?"** → Lee su implementación completa, incluyendo `try/except`.

No es admisible responder con aproximaciones ("probablemente", "supongo", "debería ser"). Si hay duda, **lee el código**. Si aún hay duda después, **dilo claramente**: "No encuentro esa parte del código" o "El código no hace lo que la documentación dice — hay una discrepancia".

Esto es especialmente crítico porque:
- Cada línea de código en este proyecto es pequeña y auditable.
- Las respuestas imprecisas sobre funcionamiento pueden llevar a cambios incorrectos.
- La documentación puede estar desactualizada; el código nunca miente.

---

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
- `code/logs/venom_engine.log` — **log de funcionamiento interno del motor** (arranque, ataques iniciados/detenidos, cambios de iptables, errores/excepciones). No es evidencia de red capturada, es diagnóstico del programa en sí. Generado por `venom_logger.py` con rotación (5 MB x 3 respaldos).

Esto es el comportamiento esperado del motor, no algo que limpiar entre ejecuciones (salvo que se quiera liberar espacio manualmente, ver `code/limpiar_logs.py`).

---

## Convenciones de Código

- **Seguir siempre PEP8** (line-length máximo 79 caracteres) en todo código Python nuevo o modificado.
- **Seguir la lógica ya aplicada en los módulos existentes** — no inventar patrones, dependencias o estructuras nuevas que puedan romper el resto de la herramienta. Antes de escribir un módulo nuevo, mirar cómo resuelven problemas similares los módulos existentes (uso de `ui_utils` para output/prompts, manejo de carpetas de evidencia, etc.) y replicar ese estilo.
- Todo script debe ir comentado por secciones explicando qué hace cada bloque, siguiendo el mismo formato de encabezado y comentarios que ya usan `arp_utils.py`, `sniffer_engine.py`, etc.
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
