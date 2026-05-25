#!/bin/bash
# Script para iniciar SysMho Venom con variables de entorno correctas

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Cargar .env
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Exportar con defaults
export DB_HOST="${DB_HOST:-localhost}"
export DB_PORT="${DB_PORT:-5432}"
export DB_NAME="${DB_NAME:-venom}"
export DB_USER="${DB_USER:-postgres}"
export DB_PASS="${DB_PASS:-}"

# Credenciales admin
export ADMIN_EMAIL="${ADMIN_EMAIL:-admin@venom.local}"
export ADMIN_PASS="${ADMIN_PASS:-admin123}"

# Configuración del servidor
export SERVER_URL="${SERVER_URL:-http://localhost:8000}"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  SysMho Venom — PHP Development Server               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Configuración:"
echo "  DB_HOST: $DB_HOST"
echo "  DB_PORT: $DB_PORT"
echo "  DB_NAME: $DB_NAME"
echo "  DB_USER: $DB_USER"
echo ""

# Verificar conexión a BD
export PGPASSWORD="$DB_PASS"
if ! psql -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ No se pudo conectar a PostgreSQL"
    echo "Verifica:"
    echo "  - PostgreSQL está corriendo"
    echo "  - Credenciales en .env son correctas"
    exit 1
fi
echo "✅ Conexión a BD OK"
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║  🌐 Servidor iniciado                                 ║"
echo "║  Acceso: $SERVER_URL                                  ║"
echo "║  Admin: $SERVER_URL/admin-panel/admin.php             ║"
echo "║  Email: $ADMIN_EMAIL                                  ║"
echo "║  Pass:  $ADMIN_PASS                                   ║"
echo "║  🛑 Ctrl+C para detener                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

exec php -S localhost:8000
