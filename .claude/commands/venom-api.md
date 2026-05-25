# /venom-api — Auditoría de endpoints API

Compara los endpoints que el frontend espera contra los que realmente existen en el backend.

## Instrucciones

### 1. Endpoints esperados por el frontend
```bash
grep -h "'/api/" admin-panel/admin.js auditor-panel/user.js viewer-panel/viewer.js | sort -u
```

### 2. Endpoints implementados en backend
```bash
ls api/ 2>/dev/null && grep -rh "case\|route\|GET\|POST\|DELETE\|PUT" api/*.php 2>/dev/null | grep "api/" | sort -u
echo "---"
ls api/ 2>/dev/null || echo "DIRECTORIO api/ NO EXISTE"
```

### 3. Cruza ambas listas y reporta
Para cada endpoint esperado por el frontend:
- ✅ Implementado — existe en `api/`
- ❌ Faltante — no existe en `api/`

### Formato de reporte
```
VENOM API AUDIT
═══════════════════════════════════════
Endpoint                    Frontend  Backend
/api/sessions               ✅        ❌
/api/sniffer/start          ✅        ❌
/api/sniffer/stop           ✅        ❌
/api/logs/list              ✅        ❌
/api/logs/download          ✅        ❌
/api/antisniffer/findings   ✅        ❌
/api/users                  ✅        ❌
/api/stats                  ✅        ❌
/api/reports/export         ✅        ❌
/api/network/scan           ✅        ❌
/api/arp/start              ✅        ❌
/api/arp/restore            ✅        ❌
═══════════════════════════════════════
Implementados: N/12
USE_MOCK:      true (desconectado) | false (conectado)
```
