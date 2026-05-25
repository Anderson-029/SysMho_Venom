# /venom-lint — Validación completa de sintaxis y estilo

Valida todo el código del proyecto antes de un commit. Cubre Python (ruff), PHP y JS.

## Instrucciones

Ejecuta cada bloque y reporta ✅ / ❌:

### Python
```bash
ruff check code/ --output-format=concise
for f in code/*.py; do python3 -m py_compile "$f" && echo "✅ $f" || echo "❌ $f"; done
```

### PHP
```bash
for f in backend/*.php admin-panel/*.php api/*.php; do
  [ -f "$f" ] || continue
  out=$(php -l "$f" 2>&1)
  echo "$out" | grep -qiE "^(Parse|Fatal) error" && echo "❌ $f: $out" || echo "✅ $f"
done
```

### JavaScript
```bash
for f in admin-panel/admin.js landing/script.js; do
  [ -f "$f" ] && node --check "$f" 2>&1 && echo "✅ $f" || echo "❌ $f"
done
```

### Coherencia crítica
```bash
# Roles inválidos (no deben existir)
grep -rn "OPERADOR\|ADMIN-VIEWER" admin-panel/

# Sesión PHP — deben aparecer las 4 variables canónicas
grep -n "user_id\|user_name\|user_role\|user_email" backend/login.php

# SQL injection check
grep -n "WHERE.*\$_POST\|WHERE.*\$email\|WHERE.*\$pass" backend/login.php

# USE_MOCK status
grep -n "USE_MOCK" admin-panel/admin.js
```

## Reporte final
```
VENOM LINT
─────────────────────────────
Python ruff:    ✅/❌
PHP sintaxis:   ✅/❌
JS sintaxis:    ✅/❌
Roles:          ✅/❌
SQL injection:  ✅/❌
USE_MOCK:       true|false
─────────────────────────────
RESULTADO: ✅ LISTO PARA COMMIT / ❌ HAY ERRORES
```
