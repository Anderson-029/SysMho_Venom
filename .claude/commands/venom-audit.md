# /venom-audit — Auditoría de seguridad del código

Revisa el motor Python en busca de vulnerabilidades o malas prácticas conocidas antes de cualquier commit importante.

## Instrucciones

Ejecuta cada check y reporta con ✅ / ⚠️ / ❌:

### 1. Credenciales hardcodeadas
```bash
grep -rn "ander123\|password.*=.*['\"][^'\"]\|pass.*=.*['\"][^'\"]" code/ 2>/dev/null | grep -v ".env\|getenv\|os.environ\|os.getenv"
```
- ✅ Sin resultados
- ❌ Credenciales expuestas en código

### 2. Subprocess bloqueante
```bash
grep -n "subprocess.run\|subprocess.call\|subprocess.Popen" code/*.py
```
- ✅ Sin resultados (todo vía `asyncio.create_subprocess_exec`)
- ❌ Hay llamadas síncronas que bloquean el event loop

### 3. Cleanup en finally (ARP + iptables)
```bash
grep -n "finally" code/venom_route.py code/arp_utils.py code/iptables_utils.py
```
- ✅ Los tres archivos tienen bloque `finally`
- ❌ Falta cleanup

### 4. check_root() antes de operaciones privilegiadas
```bash
grep -n "check_root" code/venom_route.py
```

### 5. Threads con stop_event
```bash
grep -n "threading.Event\|stop_event" code/*.py
```

### 6. db_bridge — fallo silencioso si no hay BD
```bash
grep -n "except.*psycopg2\|except.*OperationalError" code/db_bridge.py
```
- ✅ Captura errores de conexión sin interrumpir el CLI
- ❌ Sin manejo de errores de conexión

### 7. Credenciales de BD vía entorno
```bash
grep -n "os.getenv\|os.environ" code/db_bridge.py
```

## Reporte final
```
VENOM SECURITY AUDIT
════════════════════════════════════
Credenciales:       ✅/❌
Subprocess async:   ✅/❌
Cleanup finally:     ✅/❌
check_root():       ✅/❌
Threads stop_event: ✅/❌
db_bridge fallback: ✅/❌
Env variables:      ✅/❌
════════════════════════════════════
RESULTADO: ✅ SEGURO / ⚠️ REVISAR / ❌ VULNERABILIDADES PRESENTES
```
