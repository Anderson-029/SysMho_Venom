# HANDOFF — SysMho Venom

Estado del proyecto al cierre de esta sesión de trabajo. Léelo antes de retomar.

---

## Qué es el proyecto ahora

**Venom-Route volvió a ser exclusivamente la herramienta CLI original.** En esta sesión se construyó y luego se revirtió por completo una capa web (PHP + API REST + admin panel + landing en React/Three.js) — esa capa **ya no existe** en el repo. Ver `CLAUDE.md` para el estado técnico completo.

El proyecto es hoy: motor Python puro (`code/`), sin base de datos, sin backend web, sin frontend. Toda la evidencia capturada se guarda como archivos locales.

---

## Qué se hizo en esta sesión (orden cronológico)

1. **Se construyó una landing en React** (`landing-app/` → build en `landing/`) con Three.js/Framer Motion, tono presentativo, paleta `#2F4858`/`#DDFBEF` — en respuesta a un pedido explícito de rediseño total.
2. **Se arregló un bug real de login** (hash bcrypt desincronizado en la tabla `tab_usuarios`).
3. **El usuario decidió revertir todo eso**: pidió que el proyecto "vuelva a ser solamente la herramienta CLI que era al principio".
4. Se eliminó por completo: `admin-panel/`, `api/` (incl. `api/cli/`), `backend/`, `landing/`, `landing-app/`, `index.php`, `setup.sh`, `start.sh`, `kill_venom.sh`, y toda la documentación/comandos específicos de la capa web.
5. Se limpiaron archivos de captura viejos (`code/logs/`, `code/archivos_unicos/` de una prueba del 25 mayo 2026).
6. **Se eliminó también la persistencia a PostgreSQL**: `code/db_bridge.py` y todas sus llamadas en `venom_route.py`, `sniffer_engine.py`, `network_utils.py`, `anti_sniff_detector.py`; se borró `SQL/` (schema/triggers) y las bases de datos `venom` y `sysmho_venom` (esta última era un residuo de una configuración anterior con nombre distinto, sin relación con el proyecto actual).
7. Se reindexó el grafo de código (`codebase-memory-mcp`) — 118 nodos / 274 aristas, reflejando el proyecto reducido.

---

## Estado técnico actual

- **Único componente ejecutable:** `code/venom_route.py` (requiere root, red real).
- **8 módulos**, cada uno con responsabilidad única — ver tabla en `code/AGENTS.md`.
- **Sin BD, sin `.env`** (no quedan variables de entorno que configurar).
- **Persistencia:** archivos locales únicamente — `code/logs/<protocolo>/`, `code/archivos_unicos/`, `code/sniff_detection/`. Esto es el comportamiento esperado, no algo a "limpiar" entre ejecuciones salvo que se quiera liberar espacio.
- Los 8 módulos compilan sin errores de sintaxis (verificado en esta sesión).
- `ruff` no está instalado en este entorno (`command not found`) — no se pudo correr `/venom-lint` con el linter real, solo compilación de sintaxis.

## Pendientes / cosas a saber

- **Archivos `root`-owned sin resolver:** `code/__pycache__/` quedó con archivos propiedad de `root` (de una ejecución anterior con `sudo`) que ni el asistente ni el sandbox pueden borrar. Pendiente que el usuario corra manualmente:
  ```bash
  sudo rm -rf "/home/anderson/Documentos/programas personales/SysMho_Venom/code/__pycache__"
  ```
- El repo tiene un commit previo (`ad2cfdf — "actaulizacion a solamente herramienta CLI"`) ya pusheado a `main` en GitHub. **Los cambios de esta sesión posteriores a ese commit (eliminación de `db_bridge`/`SQL/`, drop de las BDs, este `HANDOFF.md`) están sin commitear todavía.**
- `.git/` pesa ~293MB por el historial de los videos/PNGs de la landing (ya eliminados del working tree pero no de la historia). No se ha tocado el historial de git — sería una operación de alto riesgo (reescritura de historia) que requiere confirmación explícita si se quiere reducir.

---

## Cómo correrlo

```bash
cd "/home/anderson/Documentos/programas personales/SysMho_Venom"

# Modo interactivo (recomendado)
sudo python3 code/venom_route.py -I

# Modo avanzado
sudo python3 code/venom_route.py -v VICTIM_IP -g GATEWAY_IP -i INTERFACE -F -M -A
```

Validación antes de commit: `/venom-lint` y `/venom-audit` (slash commands en `.claude/commands/`).
