# /venom-audit — Auditoría de seguridad del código

Revisa el código del proyecto en busca de vulnerabilidades conocidas antes de cualquier deploy o commit importante.

## Instrucciones

Ejecuta cada check y reporta con ✅ / ⚠️ / ❌:

### 1. SQL Injection (CRÍTICO)
```bash
# Buscar variables de usuario concatenadas directamente en SQL
grep -rn "\$_POST\|\$_GET\|\$_REQUEST" backend/ api/ 2>/dev/null | grep -v "prepare\|bindParam\|execute"
```
- ✅ Sin resultados — usa prepared statements
- ❌ Hay resultados — SQL injection presente

### 2. Credenciales hardcodeadas
```bash
grep -rn "ander123\|password.*=.*['\"][^'\"]\|pass.*=.*['\"][^'\"]" backend/ api/ code/ 2>/dev/null | grep -v ".env\|getenv\|os.environ"
```
- ✅ Sin resultados
- ❌ Credenciales expuestas en código

### 3. innerHTML con datos sin sanitizar
```bash
grep -rn "innerHTML.*\(data\.\|result\.\|row\.\|user\.\|item\." admin-panel/ auditor-panel/ viewer-panel/ 2>/dev/null
```
- ✅ Sin resultados (usa textContent)
- ⚠️ Hay resultados — revisar si los datos son confiables

### 4. eval() en JavaScript
```bash
grep -rn "\beval(" admin-panel/ auditor-panel/ viewer-panel/ landing/ 2>/dev/null
```
- ✅ Sin resultados
- ❌ eval() presente — XSS potencial

### 5. auth.php incluido en todas las páginas PHP
```bash
for f in admin-panel/*.php auditor-panel/*.php viewer-panel/*.php; do
  [ -f "$f" ] || continue
  grep -l "require.*auth.php" "$f" && echo "✅ $f" || echo "❌ $f — sin auth.php"
done
```

### 6. require_role() antes de lógica sensible
```bash
grep -rn "require_role" admin-panel/ auditor-panel/ viewer-panel/ api/ 2>/dev/null
```
Verificar que aparece en cada archivo PHP que maneja datos.

### 7. Secretos en variables de entorno (no hardcoded)
```bash
grep -rn "DB_PASS\|DB_USER\|getenv\|\\$_ENV" backend/config.php api/ 2>/dev/null
```
- ✅ Usa `getenv()` o `$_ENV`
- ❌ Valores directos en código

### 8. Motor Python — cleanup en finally
```bash
grep -n "finally" code/venom_route.py code/arp_utils.py
```
- ✅ Ambos archivos tienen bloque finally
- ❌ Falta cleanup

## Reporte final
```
VENOM SECURITY AUDIT
════════════════════════════════════
SQL Injection:     ✅/❌
Credenciales:      ✅/❌
innerHTML XSS:     ✅/⚠️/❌
eval() JS:         ✅/❌
Auth en PHP:       ✅/❌ (N/N archivos)
require_role():    ✅/❌
Env variables:     ✅/❌
Python cleanup:    ✅/❌
════════════════════════════════════
RESULTADO: ✅ SEGURO / ⚠️ REVISAR / ❌ VULNERABILIDADES PRESENTES
```
