# /venom-phase — Estado y trazabilidad de fases del plan

Muestra el estado detallado de las fases del PLAN.md y qué tareas están pendientes en la fase activa.

## Instrucciones

1. Lee `PLAN.md` completo
2. Identifica la fase activa (primera con tareas `[ ]` sin completar)
3. Lista las tareas completadas `[x]` y pendientes `[ ]` de esa fase
4. Muestra el bloqueo de fases siguientes

### Comando para ver tareas pendientes de cada fase
```bash
grep -n "\[ \]\|\[x\]" PLAN.md
```

### Formato de reporte
```
VENOM PLAN — ESTADO DE FASES
══════════════════════════════════════
Fase 0 — Línea Base:     🟢 / 🟡 / 🔴
  [x] F0-01 login.php prepared statements
  [ ] F0-02 agregar user_email a sesión
  ...

Fase 1 — API REST:       ⚫ BLOQUEADA (espera Fase 0)
Fase 2 — Bridge Python:  ⚫ BLOQUEADA (espera Fase 0)
Fase 3 — Sin mocks:      ⚫ BLOQUEADA (espera Fases 1+2)
Fase 4 — UI/UX:          ⚫ BLOQUEADA (espera Fase 3)
Fase 5 — Real-time SSE:  ⚫ BLOQUEADA (espera Fases 3+4)
══════════════════════════════════════
Fase activa: 0 — N/7 tareas completadas
Siguiente tarea: F0-02 — agregar user_email a sesión en login.php
```

Si todas las tareas de una fase están en `[x]`, marcar esa fase como 🟢 COMPLETADA en el reporte y señalar cuál es la siguiente fase activa.
