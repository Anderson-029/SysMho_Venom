# SysMho Venom — Quick Start

## 🚀 Inicio en 30 segundos

### Opción A: Script automático (recomendado)
```bash
cd ~/Documentos/programas\ personales/SysMho_Venom
./setup.sh
```

El script va a:
1. ✅ Verificar requisitos (PHP, PostgreSQL, Python)
2. ✅ Crear BD `venom` si no existe
3. ✅ Ejecutar schema SQL (12 tablas con relaciones)
4. ✅ Crear usuario admin (`admin@venom.local` / `admin123`)
5. ✅ Levantar PHP dev server en `http://localhost:8000`

**Acceso al sistema:**
1. Abre navegador: `http://localhost:8000/landing/index.html`
2. Click en **"Entrar"** (aparece modal de login)
3. Email: `admin@venom.local`
4. Contraseña: `admin123`
5. Click **Entrar** → Redirige al dashboard admin
6. ¡Sistema listo para usar!

---

### Opción B: Manual (si el script falla)

**1. Configurar variables en .env:**
```bash
# En la raíz del proyecto, edita .env:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=venom         # ⚠️ IMPORTANTE: minúsculas
DB_USER=postgres
DB_PASS=ander123      # Tu contraseña de PostgreSQL
```

**2. Crear BD e inicializar schema:**
```bash
export PGPASSWORD="ander123"
psql -h localhost -U postgres -c "CREATE DATABASE venom;"
psql -h localhost -U postgres -d venom < SQL/DB.sql
```

**3. Crear usuario admin:**
```bash
# Generar hash (contraseña: admin123)
HASH=$(php -r 'echo password_hash("admin123", PASSWORD_BCRYPT);')

# Insertar usuario
export PGPASSWORD="ander123"
psql -h localhost -U postgres -d venom << EOF
DELETE FROM tab_usuarios WHERE email_usuario = 'admin@venom.local';
INSERT INTO tab_usuarios (nombre, email_usuario, passwd_hash, rol, activo, usr_insert, fec_insert)
VALUES ('Anderson', 'admin@venom.local', '$HASH', 'admin', true, 'setup', NOW());
EOF
```

**4. Levantar servidor PHP:**
```bash
cd /home/anderson/Documentos/programas\ personales/SysMho_Venom
php -S localhost:8000
```

**5. Acceder:**
- Navegador: `http://localhost:8000/landing/index.html`
- Login modal: email `admin@venom.local`, contraseña `admin123`

---

## 🔍 Verificación rápida

Después de iniciar, comprueba:

### En el navegador (F12 DevTools):
- **Console**: sin errores 404
- **Network**: Requests a `/landing/login.php` → 302 redirect
- **Admin Panel**: Sidebar con menú de navegación visible

### En el dashboard:
1. **Overview**: KPIs mostrados (Sesiones, Hosts, Protocolos, Sniffers)
2. **Usuarios**: Sección funcional (CRUD de usuarios)
3. **Auditoría**: Trail de eventos del sistema
4. **Operaciones**: Panel para iniciar sesiones MITM
5. **Logs & Evidencias**: Almacenamiento de capturas

---

## 🐛 Si algo falla

| Error | Solución |
|---|---|
| **"Redirige a landing después de login"** | El script.js estaba bloqueando el POST. Ya está arreglado. Borra cache del navegador (Ctrl+F5). |
| **"FATAL: database venom does not exist"** | Asegúrate que PostgreSQL está corriendo: `psql -U postgres -c "SELECT 1"` |
| **"FATAL: no password supplied"** | El .env no está siendo leído. config.php ahora lo carga automáticamente. Reinicia el PHP server. |
| **"Login rechazado"** | Verificar usuario: `psql -U postgres -d venom -c "SELECT email_usuario FROM tab_usuarios"` |
| **Página en blanco** | Revisar output de `php -S localhost:8000` en la terminal |
| **API retorna 'No autorizado'** | Necesitas estar logueado. El login establece PHPSESSID cookie. |

---

## 📚 Próximos pasos

### Fase 1: Pruebas manuales en la interfaz (EN PROGRESO)
- ✅ Login funcional desde landing page
- ✅ Dashboard admin accesible
- ⏳ **Próximo**: Probar controles de operaciones (crear sesiones MITM)
- ⏳ Crear datos de prueba en el dashboard
- ⏳ Explorar todas las vistas (Usuarios, Auditoría, Reportes)

### Fase 2: Pruebas CLI + integración BD
- ⏳ Ejecutar motor Python: `sudo python3 code/venom_route.py -I`
- ⏳ Capturar tráfico real
- ⏳ Verificar que datos se registren en la BD
- ⏳ Ver resultados en tiempo real en el dashboard

### Fase 3: Automatización completa
- ⏳ Flujo MITM → BD → Dashboard sin intervención
- ⏳ Reportes generados automáticamente
- ⏳ Exportación de evidencias

---

## ⚙️ Configuración (opcional)

Si PostgreSQL no está en `localhost:5432`, edita el archivo `.env`:
```bash
DB_HOST=tuhost.com
DB_PORT=5432
DB_NAME=venom           # ⚠️ siempre minúsculas
DB_USER=usuario
DB_PASS=contraseña
```

Luego reinicia el PHP server:
```bash
php -S localhost:8000
```

---

## 📖 Documentación técnica

- **CLAUDE.md** - Arquitectura del proyecto, stack tecnológico, estructura de carpetas
- **PLAN.md** - Fases de desarrollo, roadmap completo
- **.claude/rules/** - Reglas de desarrollo por componente (Python, PHP, JS)

---

## 🛠️ Archivos clave

| Archivo | Propósito |
|---------|-----------|
| `.env` | Credenciales y configuración de BD |
| `backend/config.php` | Conexión PostgreSQL (lee .env automáticamente) |
| `backend/login.php` | Autenticación (verifica contraseña con bcrypt) |
| `landing/login.php` | Bridge entre landing y backend |
| `landing/script.js` | Login modal y navegación de landing |
| `admin-panel/admin.php` | Dashboard principal (requiere sesión) |
| `api/index.php` | Router REST (auth requerida para todos los endpoints) |
| `SQL/DB.sql` | Schema de 12 tablas con triggers de auditoría |
