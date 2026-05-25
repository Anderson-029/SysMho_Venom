# STATUS — SysMho Venom (24 May 2026)

## 🟢 Sistema Operativo

```
✅ PostgreSQL 16        → Corriendo en :5432
✅ PHP 8.3 Dev Server   → Corriendo en localhost:8000
✅ Base de Datos        → 12 tablas inicializadas + triggers
✅ Usuario Admin        → anderson / admin@venom.local / admin123
✅ Autenticación        → Funcional (bcrypt)
✅ Dashboard Admin      → Accesible y operativo
```

## 🚀 Acceso Rápido

| Componente | URL | Estado |
|-----------|-----|--------|
| **Landing Page** | http://localhost:8000/landing/index.html | ✅ Login modal |
| **Dashboard Admin** | http://localhost:8000/admin-panel/admin.php | ✅ Requiere sesión |
| **API REST** | http://localhost:8000/api/ | ✅ Requiere autenticación |
| **Admin Panel** | http://localhost:8000/admin-panel/admin.php | ✅ Completo |

## 🔧 Archivos Modificados Recientemente

| Archivo | Cambio | Fecha |
|---------|--------|-------|
| `.env` | DB_NAME: VENOM → venom (minúsculas) | 24 May |
| `backend/config.php` | Auto-carga .env con parse_ini_file() | 24 May |
| `landing/login.php` | Creado como bridge al backend | 24 May |
| `landing/script.js` | Login form hace POST real (no mock) | 24 May |
| `QUICKSTART.md` | Actualizado con flujo de login correcto | 24 May |
| `CLAUDE.md` | Documentado cambios en PHP y DB | 24 May |
| `PLAN.md` | Añadida Fase 6 (Pruebas Manuales) | 24 May |

## 📊 Base de Datos

```sql
-- Conectar a la BD
export PGPASSWORD="ander123"
psql -h localhost -U postgres -d venom

-- Verificar tablas
\dt

-- Usuario admin
SELECT email_usuario, rol, activo FROM tab_usuarios;
```

**12 Tablas:**
1. `tab_usuarios` - Cuentas admin
2. `tab_alcances` - Scopes autorizados
3. `tab_runners` - Agentes/runners
4. `tab_sesiones` - Sesiones MITM
5. `tab_artefactos` - Evidencias capturadas
6. `tab_detecciones` - Hallazgos anti-sniffer
7. `tab_eventos_sesion` - Auditoría de eventos
8. `tab_protocolos` - Catálogo de protocolos
9. `tab_tipo_evidencia` - Tipos de evidencia
10. `tab_stats_protocolo` - Estadísticas
11. `tab_scan_hosts` - Hosts descubiertos
12. `tokens_invitacion` - Invitations (single-admin)

## 🐛 Problemas Corregidos

### Problema 1: Database Connection Fallaba
**Síntoma:** `pg_connect()` retornaba error "no password supplied"
**Causa:** getenv() no devolvía variables de entorno en PHP
**Solución:** config.php ahora lee `.env` directamente con parse_ini_file()

### Problema 2: Login No Redirigía al Dashboard
**Síntoma:** Enviaba POST pero volvía a la landing
**Causa:** JavaScript estaba bloqueando el formulario (preventDefault) pero no hacía POST real
**Solución:** script.js ahora hace fetch() real a `/landing/login.php` y sigue redirects

### Problema 3: Database Case Sensitivity
**Síntoma:** Conectar a "VENOM" fallaba, pero "venom" sí funcionaba
**Causa:** PostgreSQL convierte identificadores a minúsculas automáticamente
**Solución:** Estandarizar a `DB_NAME=venom` en .env

## 📋 Próximos Pasos

### Fase 6: Pruebas Manuales (EN PROGRESO)
1. ✅ Acceso al dashboard verificado
2. ⏳ Probar todos los controles
3. ⏳ Inyectar datos de prueba
4. ⏳ Validar flujos completos

### Fase 7: Integración CLI
1. Ejecutar motor Python: `sudo python3 code/venom_route.py -I`
2. Capturar tráfico en red real
3. Verificar datos en BD
4. Visualizar en dashboard

## 📚 Documentación

- **QUICKSTART.md** - Cómo poner en marcha el sistema (30 segundos)
- **CLAUDE.md** - Arquitectura técnica, stack, convenciones
- **PLAN.md** - Roadmap completo con 7 fases
- **STATUS.md** - Este archivo (estado actual)

## 🛠️ Comandos Útiles

```bash
# Iniciar todo
cd "/home/anderson/Documentos/programas personales/SysMho_Venom"
./setup.sh

# O manualmente
php -S localhost:8000

# Conectar a BD
export PGPASSWORD="ander123"
psql -h localhost -U postgres -d venom

# Motor Python (requiere sudo)
sudo python3 code/venom_route.py -I
```

## 🔐 Credenciales

| Servicio | Usuario | Contraseña | Host |
|----------|---------|-----------|------|
| **PostgreSQL** | postgres | ander123 | localhost:5432 |
| **Admin Venom** | admin@venom.local | admin123 | localhost:8000 |

## 📞 Support

- Revisar logs PHP: `tail -f /tmp/php_server.log`
- Revisar BD: `psql -U postgres -d venom`
- Revisar errores JS: F12 → Console en navegador
