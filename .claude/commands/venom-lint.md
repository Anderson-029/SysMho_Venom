# /venom-lint — Validación completa de sintaxis y estilo

Valida el motor Python antes de un commit.

## Instrucciones

Ejecuta cada bloque y reporta ✅ / ❌:

### Python
```bash
ruff check code/ --output-format=concise
for f in code/*.py; do python3 -m py_compile "$f" && echo "✅ $f" || echo "❌ $f"; done
```

### Coherencia crítica
```bash
# Cleanup en finally (ARP + iptables)
grep -n "finally" code/venom_route.py code/arp_utils.py

# check_root() antes de operaciones con privilegios
grep -n "check_root" code/venom_route.py
```

## Reporte final
```
VENOM LINT
─────────────────────────────
Python ruff:    ✅/❌
Python compile: ✅/❌
Cleanup finally:✅/❌
check_root():   ✅/❌
─────────────────────────────
RESULTADO: ✅ LISTO PARA COMMIT / ❌ HAY ERRORES
```
