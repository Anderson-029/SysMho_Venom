#!/bin/bash
# ========================================================================
# SysMho Venom — Setup Automático
# Inicializa BD, crea usuario admin y levanta el servidor PHP
# ========================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  SysMho Venom — Setup Automático                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Verificar requisitos ────────────────────────────────────
echo "[1/6] Verificando requisitos..."
for cmd in php psql python3; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ $cmd no está instalado. Instálalo y vuelve a intentar."
        exit 1
    fi
done
echo "✅ PHP, PostgreSQL, Python3 disponibles"
echo ""

# ── Step 2: Configurar env vars ─────────────────────────────────────
echo "[2/6] Configurando variables de entorno..."

# Cargar desde .env si existe
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
    echo "  ✅ Cargado desde .env"
fi

# Usar valores del .env o defaults
export DB_HOST="${DB_HOST:-localhost}"
export DB_PORT="${DB_PORT:-5432}"
export DB_NAME="${DB_NAME:-venom}"
export DB_USER="${DB_USER:-postgres}"
export DB_PASS="${DB_PASS:-}"
export PGPASSWORD="$DB_PASS"

# Credenciales admin
export ADMIN_EMAIL="${ADMIN_EMAIL:-admin@venom.local}"
export ADMIN_PASS="${ADMIN_PASS:-admin123}"
export ADMIN_NAME="${ADMIN_NAME:-Anderson}"

# Configuración del servidor
export SERVER_HOST="${SERVER_HOST:-localhost}"
export SERVER_PORT="${SERVER_PORT:-8000}"
export SERVER_URL="${SERVER_URL:-http://localhost:8000}"

echo "  DB_HOST=$DB_HOST"
echo "  DB_PORT=$DB_PORT"
echo "  DB_NAME=$DB_NAME"
echo "  DB_USER=$DB_USER"
echo "✅ Env vars configuradas"
echo ""

# ── Step 3: Crear BD y schema ───────────────────────────────────
echo "[3/6] Inicializando base de datos..."

# Crear BD si no existe
psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" 2>/dev/null | grep -q 1 || \
  psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -c "CREATE DATABASE $DB_NAME" 2>/dev/null

echo "  Base de datos: ✅"

# Ejecutar schema
if [ -f "SQL/DB.sql" ]; then
    psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$DB_NAME" < SQL/DB.sql > /dev/null 2>&1
    echo "  Schema: ✅"
else
    echo "❌ SQL/DB.sql no encontrado"
    exit 1
fi

# Verificar tablas
TABLE_COUNT=$(psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$DB_NAME" -tc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null)
echo "  Tablas creadas: $TABLE_COUNT ✅"
echo ""

# ── Step 4: Crear usuario admin ─────────────────────────────────────
echo "[4/6] Configurando usuario admin..."

# Generar hash bcrypt con contraseña del .env
HASH=$(php -r "echo password_hash('$ADMIN_PASS', PASSWORD_BCRYPT);")

# Insertar usuario
psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$DB_NAME" <<EOF > /dev/null 2>&1
DELETE FROM tab_usuarios WHERE email_usuario = '$ADMIN_EMAIL';
INSERT INTO tab_usuarios (nombre, email_usuario, passwd_hash, rol, activo, usr_insert, fec_insert)
VALUES ('$ADMIN_NAME', '$ADMIN_EMAIL', '$HASH', 'admin', true, 'setup', NOW());
EOF

echo "  Usuario: $ADMIN_NAME ($ADMIN_EMAIL)"
echo "  Contraseña: $ADMIN_PASS"
echo "✅ Usuario admin creado"
echo ""

# ── Step 5: Verificar directorio api ────────────────────────────────
echo "[5/6] Verificando estructura del proyecto..."

DIRS=("api" "backend" "admin-panel" "code" "SQL" "landing")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/"
    else
        echo "  ❌ $dir/ falta"
        exit 1
    fi
done
echo ""

# ── Step 6: Levantar PHP dev server ─────────────────────────────────
echo "[6/6] Iniciando servidor PHP..."
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETADO                                  ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  📍 Acceso:                                           ║"
echo "║     $SERVER_URL/admin-panel/admin.php"
echo "║                                                        ║"
echo "║  👤 Credenciales:                                     ║"
echo "║     Email: $ADMIN_EMAIL"
echo "║     Pass:  $ADMIN_PASS"
echo "║                                                        ║"
echo "║  🛑 Para detener: Ctrl+C                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

exec php -S localhost:8000
