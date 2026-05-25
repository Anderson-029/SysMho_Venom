# Reglas — SysMho Venom Web

## Principio Fundamental (NO NEGOCIABLE)
Cada cambio debe garantizar:
1. **Coherencia** — Mismo patrón en todos los archivos del mismo tipo
2. **Congruencia** — Variables de sesión, roles, endpoints y nombres de tablas coinciden en toda la codebase
3. **Funcionalidad** — Nada se deja a medias; si no está terminado, no se merge
4. **Estabilidad** — Cero regressions; el motor Python CLI nunca se rompe

---

## Fases — Respetar Orden

Ver `PLAN.md` en raíz. No implementar Fase N sin completar Fase N-1.
- Motor Python (`code/`) = ESTABLE. No modificar salvo bugs críticos o Fase 2.
- `USE_MOCK = true` hasta que Fase 1 + 2 estén completas.

---

## PHP — Reglas de Endpoints REST

### Estructura obligatoria en cada endpoint `/api/*.php`
```php
<?php
require_once __DIR__ . '/../api/middleware.php';  // auth + headers JSON
// Solo si necesita rol específico:
require_role(['admin']);

header('Content-Type: application/json');

// lógica
echo json_encode(['data' => $resultado, 'ok' => true]);
```

### Reglas
- **Siempre prepared statements**: `$stmt = $pdo->prepare("SELECT ... WHERE id = ?")` + `$stmt->execute([$id])`
- **Nunca concatenar** variables de usuario en SQL
- **Roles válidos**: solo `admin`, `auditor`, `viewer` — nunca `OPERADOR`, `ADMIN-VIEWER`
- **Respuesta siempre JSON**: `{"data": ..., "ok": true}` o `{"error": "...", "ok": false}`
- **HTTP status codes correctos**: 200, 201, 400, 401, 403, 404, 500

### Variables de sesión canónicas (PHP)
```php
$_SESSION["user_id"]     // UUID
$_SESSION["user_name"]   // nombre display
$_SESSION["user_role"]   // admin | auditor | viewer (lowercase)
$_SESSION["user_email"]  // email
```
Estas 4 y solo estas 4. No crear variables de sesión nuevas sin actualizar auth.php.

---

## JavaScript — Reglas de Frontend

### Flag de mock
```javascript
const USE_MOCK = false;  // SIEMPRE false cuando endpoints existen
```
Solo `true` durante desarrollo local sin backend. Nunca commitear `true` en Fase 3+.

### Roles en JS (canónicos, lowercase)
```javascript
const ROLES = { ADMIN: 'admin', AUDITOR: 'auditor', VIEWER: 'viewer' };
```
Nunca usar `OPERADOR`, `ADMIN-VIEWER`, ni strings distintos a los 3 anteriores.

### Fetch a API
```javascript
// Patrón obligatorio para llamadas a /api/
async function apiGet(endpoint) {
    const res = await fetch(endpoint);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
}
```
Siempre manejar errores con try/catch y mostrar con `showToast(msg, 'error')`.

### Estado de carga
Siempre mostrar loading state antes de fetch, y vaciar al completar:
```javascript
container.innerHTML = '<div class="loading">Cargando...</div>';
```

---

## CSS — Design System Venom

### Tokens base (NO cambiar sin actualizar los 3 paneles)
```css
--bg: #0d1512           /* fondo */
--surface: #0f1b17      /* cards/sidebar */
--primary: #34d399      /* verde = acción/éxito */
--accent: #60a5fa       /* azul = información */
--danger: #f87171       /* rojo = alerta/peligro */
--warning: #fbbf24      /* amarillo = precaución */
```

### Convención de clases
- `.admin-only` — elementos solo visibles/activos para admin
- `.auditor-only` — elementos solo para auditor
- `.read-only` — elementos deshabilitados para viewer
- `.is-active` — estado activo en nav
- `.is-visible` — vista activa en SPA

---

## Python — Motor (ESTABILIZADO)

El código en `code/` es ESTABLE. Reglas para cualquier modificación:
- Cleanup SIEMPRE en bloque `finally` (ARP + iptables)
- Threads con `threading.Event` como stop signal
- `check_root()` antes de cualquier operación con privilegios
- `ruff check code/` debe pasar sin errores
- `db_bridge.py` es el ÚNICO módulo que puede tocar PostgreSQL desde Python

---

## SQL — Base de Datos

- **Nunca DELETE físico** — soft delete con `fec_delete = NOW(), usr_delete = current_user`
- **PKs**: UUID con `gen_random_uuid()` o IDENTITY GENERATED
- **Nuevas tablas**: incluir las 6 columnas de auditoría + FK con `ON DELETE RESTRICT`
- **Triggers**: cualquier tabla con UPDATE debe tener trigger de auditoría
- **Catálogos** (`tab_Protocolos`, `tab_Tipo_evidencia`): populated en `DB.sql` con INSERT iniciales

---

## Seguridad — Checklist Antes de Commit

- [ ] Sin credenciales hardcodeadas (ni en PHP, ni en JS, ni en Python)
- [ ] Todos los SQL con prepared statements
- [ ] `require_once '../backend/auth.php'` en cada PHP nuevo
- [ ] `require_role(...)` antes de operaciones sensibles
- [ ] Sin `innerHTML` con datos de usuario (usar `textContent` o sanitizar)
- [ ] Sin `eval()` en JavaScript
- [ ] Logs sin passwords ni tokens
