# /venom-mock — Revisar o cambiar el estado de USE_MOCK

Muestra el estado actual de USE_MOCK en los 3 paneles. Opcionalmente cambia el valor si se pasa argumento.

## Uso
- `/venom-mock` — solo muestra estado actual
- `/venom-mock on` — activa mocks (USE_MOCK = true) en los 3 paneles
- `/venom-mock off` — desactiva mocks (USE_MOCK = false) en los 3 paneles

## Instrucciones

### 1. Mostrar estado actual siempre
```bash
grep -n "USE_MOCK" admin-panel/admin.js auditor-panel/user.js viewer-panel/viewer.js
```

### 2. Si el argumento es "off"
Verificar primero que los endpoints existen antes de desactivar mocks:
```bash
ls api/ 2>/dev/null || echo "ADVERTENCIA: api/ no existe — los paneles fallarán sin mocks"
```

Si `api/` existe, editar los 3 archivos cambiando `USE_MOCK = true` por `USE_MOCK = false`.

**IMPORTANTE:** Solo desactivar mocks si Fases 1 y 2 están completas (api/ existe y db_bridge.py existe). Si no, advertir al usuario y no hacer el cambio.

### 3. Si el argumento es "on"
Editar los 3 archivos cambiando `USE_MOCK = false` por `USE_MOCK = true`.
Útil para volver a desarrollo local sin backend.

### 4. Mostrar estado final después de cualquier cambio
```bash
grep -n "USE_MOCK" admin-panel/admin.js auditor-panel/user.js viewer-panel/viewer.js
```

## Reporte
```
VENOM MOCK STATUS
─────────────────────────────
admin-panel/admin.js:   USE_MOCK = true|false
auditor-panel/user.js:  USE_MOCK = true|false
viewer-panel/viewer.js: USE_MOCK = true|false
─────────────────────────────
Estado: MOCK ACTIVO (desarrollo) | REAL (producción)
api/ existe: ✅/❌
db_bridge.py existe: ✅/❌
```
