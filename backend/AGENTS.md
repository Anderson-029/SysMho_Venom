# AGENTS.md — backend/ (PHP + PostgreSQL)

## Responsabilidad

Autenticación, gestión de sesiones PHP y conexión a la base de datos PostgreSQL. Este módulo valida y restringe los accesos únicamente al rol de administrador.

---

## Archivos y Función

| Archivo | Función |
|---------|---------|
| `config.php` | Conecta a PostgreSQL usando variables de entorno (`getenv`) y crea la conexión `$conn` global. |
| `auth.php` | Middleware que verifica sesión activa del rol `admin`. Redirige si el usuario no tiene permisos de administrador. |
| `login.php` | Procesa POST login con prepared statements y password_verify, setea `$_SESSION` y redirige a `admin-panel/admin.php`. |
| `logout.php` | Destruye la sesión de administrador y redirige a la landing page. |

---

## Flujo de Autenticación (Single Admin)

```
POST /backend/login.php
  → query tab_Usuarios por email (vía pg_prepare/pg_execute)
  → verificar estado activo e inicio de sesión
  → password_verify($_POST['password'], hash_bd)
  → $_SESSION['user_id'], $_SESSION['user_role'] = 'admin', $_SESSION['user_name'], $_SESSION['user_email']
  → Redirección única a /admin-panel/admin.php
```

---

## Reglas para Agentes

### Seguridad (CRÍTICO)
- **Nunca** registrar la contraseña `$_POST['password']` ni su hash en salidas de depuración.
- Usar `password_verify()` para comparar contraseñas — nunca comparar hashes directamente.
- Preparar SIEMPRE las consultas a la base de datos utilizando prepared statements (`pg_prepare` + `pg_execute`) para evitar inyección SQL.
- El rol permitido por la base de datos y la sesión es exclusivamente `'admin'`.

### Patrón Obligatorio para Todo Endpoint PHP Nuevo (Filtro Admin)
```php
<?php
require_once __DIR__ . '/../backend/auth.php'; // Deniega acceso si no es admin
// lógica del script aquí
?>
```

### Variables de Sesión Disponibles
```php
$_SESSION['user_id']     // UUID del administrador
$_SESSION['user_role']   // 'admin' (único valor permitido)
$_SESSION['user_name']   // Nombre del administrador
$_SESSION['user_email']  // Correo del administrador
```

---

## Credenciales de BD
Las credenciales de BD se extraen dinámicamente usando `getenv()` en `config.php`:
- `DB_HOST` (por defecto `localhost`)
- `DB_PORT` (por defecto `5432`)
- `DB_NAME` (por defecto `VENOM`)
- `DB_USER` (por defecto `postgres`)
- `DB_PASS` (por defecto `""`)

---

## Validación Antes de Commit

```bash
php -l backend/config.php
php -l backend/auth.php
php -l backend/login.php
php -l backend/logout.php
```
