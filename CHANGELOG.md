# CHANGELOG — SysMho Venom

## [24 May 2026] - Sesión de Estabilización

### 🔧 Cambios Implementados

#### Backend PHP
- **backend/config.php**
  - Agregado auto-carga de `.env` con `parse_ini_file()`
  - Estandarizado DB_NAME a minúsculas (`venom`)
  - Fallback para variables de entorno: primero getenv(), luego .env

- **landing/login.php** (NUEVO)
  - Archivo bridge que redirige al `backend/login.php`
  - Permite que el formulario de la landing apunte a `action="login.php"`

#### Frontend JavaScript
- **landing/script.js**
  - Arreglado event listener de formulario de login
  - Implementado fetch() real a `/landing/login.php` (no más mock)
  - Manejo de redirects HTTP 302 al dashboard admin
  - Validación de email y contraseña antes de enviar

#### Base de Datos
- **.env**
  - Cambio: `DB_NAME=VENOM` → `DB_NAME=venom` (minúsculas)
  - Razón: PostgreSQL convierte a minúsculas automáticamente
  - Consistencia: evitar errores de case-sensitivity

#### Documentación
- **QUICKSTART.md**
  - Actualizado flujo de acceso: landing → modal login → dashboard
  - Clarificación de rutas y configuración
  - Expandido troubleshooting con soluciones para nuevos problemas

- **CLAUDE.md**
  - Expandida tabla de 12 tablas de BD
  - Actualizado section de PHP con info sobre config.php
  - Documentado flujo de login con sesiones PHP
  - Añadida sección "Estado Actual del Proyecto"

- **PLAN.md**
  - Agregado resumen de cambios del 24 May
  - Añadida Fase 6: Pruebas Manuales (EN PROGRESO)
  - Actualizada tabla de Control de Progreso
  - Clarificada Fase 7: Integración CLI

- **STATUS.md** (NUEVO)
  - Resumen ejecutivo del estado del sistema
  - Acceso rápido a URLs y credenciales
  - Tabla de problemas corregidos
  - Comandos útiles y troubleshooting

- **CHANGELOG.md** (ESTE ARCHIVO)
  - Registro de cambios realizados

### 🐛 Bugs Corregidos

1. **Database Connection Failure**
   - Problema: `getenv()` retornaba valores vacíos en PHP
   - Solución: config.php lee `.env` directamente
   - Impacto: Login ahora funciona sin requerir variables de entorno shell

2. **Login Form No Hacía POST Real**
   - Problema: JavaScript bloqueaba formulario pero no lo enviaba
   - Solución: Implementado fetch() a `/landing/login.php`
   - Impacto: Usuario puede hacer login desde landing page

3. **Database Case Sensitivity**
   - Problema: Conectar a `VENOM` fallaba, `venom` funcionaba
   - Solución: Estandarizar a minúsculas en .env y config.php
   - Impacto: Coherencia en toda la aplicación

### ✅ Validaciones Completadas

```bash
# Verificación de sistema funcional
✅ PostgreSQL corriendo: localhost:5432
✅ PHP Server corriendo: localhost:8000
✅ BD inicializada: 12 tablas + triggers
✅ Usuario admin activo: admin@venom.local
✅ Login funcional: Flujo completo landing → dashboard
✅ API respondiendo: /api/stats retorna JSON autenticado
✅ Dashboard accesible: Requiere sesión válida
```

### 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| Archivos modificados | 6 |
| Bugs corregidos | 3 |
| Documentos actualizados | 4 |
| Nuevos archivos | 2 (STATUS.md, CHANGELOG.md) |
| Líneas de código PHP modificadas | ~20 |
| Líneas de código JS modificadas | ~15 |

### 🚀 Estado del Sistema

```
┌─────────────────────────────────────┐
│  SysMho Venom — Estado: OPERATIVO   │
├─────────────────────────────────────┤
│ ✅ Base de datos        → INIT      │
│ ✅ Autenticación        → WORKING   │
│ ✅ Dashboard Admin      → ACCESSIBLE│
│ ✅ API REST             → AUTH OK   │
│ ✅ Landing Page         → LOGIN OK  │
│ 🟡 Motor Python (CLI)   → READY     │
└─────────────────────────────────────┘
```

### 📝 Notas de Desarrollo

- **Config Management**: Cambiar a lectura de .env en PHP ha simplificado el despliegue
- **Session Handling**: PHP sessions funcionan correctamente con PHPSESSID
- **Error Handling**: Los errores de BD ahora son claros (formato JSON)
- **Frontend-Backend**: El flujo login ahora es coherente y predecible

### 🔐 Seguridad

- ✅ Prepared statements en todas las queries SQL
- ✅ Passwords hasheados con bcrypt
- ✅ Sesiones con timeout configurable
- ✅ Credenciales en .env (no en código)
- ⚠️ HTTPS no implementado aún (dev solo)

### ⏭️ Próximas Fases

1. **Fase 6** (Actual): Pruebas manuales de interfaz
2. **Fase 7** (Próxima): Integración con motor Python CLI
3. **Fase 8** (Futura): Automatización y reporte

---

**Verificado y funcional por:** Anderson  
**Fecha:** 24 May 2026  
**Versión anterior:** N/A (Primera sesión de estabilización)  
**Siguiente review:** Después de Fase 6 (Pruebas Manuales)
