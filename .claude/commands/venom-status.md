# /venom-status — Estado general del proyecto

Ejecuta una revisión rápida del estado actual del proyecto SysMho Venom.
Muestra qué está en mock, qué fase está activa, y si hay problemas de coherencia.

## Instrucciones

Corre los siguientes checks en orden y reporta el resultado con ✅ / ⚠️ / ❌:

### 1. Estado de mocks
```bash
grep -n "USE_MOCK" admin-panel/admin.js
```
- ✅ si es `false`
- ⚠️ si es `true` (esperado hasta Fase 3)

### 2. Coherencia de roles en JS
```bash
grep -rn "OPERADOR\|ADMIN-VIEWER\|OPERATOR" admin-panel/admin.js
```
- ✅ si no hay resultados
- ❌ si hay — roles inválidos presentes

### 3. SQL injection en login.php
```bash
grep -n "\$email\|\$_POST\[" backend/login.php
```
- ✅ si usa prepared statements (`pg_prepare`, `pg_execute`)
- ❌ si concatena variables directamente en SQL

### 4. Endpoints API existentes
```bash
ls api/ 2>/dev/null || echo "DIRECTORIO api/ NO EXISTE"
```
- ✅ si existe `api/` con archivos PHP (sessions, logs, stats, etc.)
- ❌ si no existe (Fase 1 pendiente)

### 5. Bridge Python-BD
```bash
ls code/db_bridge.py 2>/dev/null || echo "db_bridge.py NO EXISTE"
```
- ✅ si existe
- ❌ si no (Fase 2 pendiente)

### 6. Triggers SQL
```bash
wc -l SQL/funcion_auditoria_y_triggers.sql
```
- ✅ si tiene contenido real (>5 líneas)
- ❌ si está vacío

### 7. Sintaxis PHP
```bash
for f in backend/*.php admin-panel/*.php api/*.php; do
  [ -f "$f" ] || continue
  php -l "$f" 2>&1 | grep -v "No syntax errors"
done
```
- ✅ si no hay output (sin errores)
- ❌ si hay errores de sintaxis

### 8. Motor Python
```bash
ruff check code/ --output-format=concise 2>&1 | head -20
```
- ✅ sin errores
- ❌ si hay warnings/errors

### 9. Fase activa
Lee `PLAN.md` y reporta qué fase está en progreso (🟡) y cuáles están pendientes (🔴).

---

Al finalizar, muestra un resumen tipo:
```
═══════════════════════════════
 VENOM STATUS — [fecha]
═══════════════════════════════
Fase activa: 3 — Frontend Real
Mocks:       ⚠️  USE_MOCK=true (admin-panel)
Roles:       ✅  Coherentes
SQL inject:  ✅  login.php usa prepared statements
API /api/:   ✅  Existe (11 endpoints)
db_bridge:   ✅  Existe
Triggers:    ✅  67 líneas
PHP sintaxis:✅  Sin errores
Python:      ✅  Sin errores ruff
═══════════════════════════════
```
