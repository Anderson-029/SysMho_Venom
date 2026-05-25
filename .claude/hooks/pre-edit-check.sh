#!/bin/bash
# Hook: validación antes de editar archivos PHP o Python
# Se ejecuta antes de cualquier Edit en archivos del proyecto

FILE="$1"
EXT="${FILE##*.}"

case "$EXT" in
  php)
    php -l "$FILE" 2>&1
    if [ $? -ne 0 ]; then
      echo "ERROR: Sintaxis PHP inválida en $FILE"
      exit 1
    fi
    # Verificar que archivos PHP (no backend/) incluyan auth.php
    if [[ "$FILE" != *"backend/"* ]] && [[ "$FILE" != *"api/"* ]]; then
      if ! grep -q "require.*auth.php" "$FILE" 2>/dev/null; then
        echo "WARNING: $FILE no incluye auth.php — verificar si es página protegida"
      fi
    fi
    ;;
  py)
    python3 -m py_compile "$FILE" 2>&1
    if [ $? -ne 0 ]; then
      echo "ERROR: Sintaxis Python inválida en $FILE"
      exit 1
    fi
    ;;
esac

exit 0
