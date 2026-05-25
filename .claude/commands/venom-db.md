# /venom-db — Estado de la base de datos

Inspecciona el estado real de PostgreSQL: tablas existentes, datos, triggers y catálogos.

## Instrucciones

### 1. Verificar conexión y tablas
```bash
psql -U postgres -d venom -c "\dt" 2>&1
```

### 2. Conteo de filas por tabla
```bash
psql -U postgres -d venom -c "
SELECT
  schemaname,
  tablename,
  n_live_tup AS filas
FROM pg_stat_user_tables
ORDER BY tablename;
" 2>&1
```

### 3. Triggers existentes
```bash
psql -U postgres -d venom -c "
SELECT trigger_name, event_object_table, event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table;
" 2>&1
```

### 4. Catálogos poblados
```bash
psql -U postgres -d venom -c "SELECT id_protocolo, nombre FROM tab_Protocolos LIMIT 10;" 2>&1
psql -U postgres -d venom -c "SELECT id_tipo, nombre FROM tab_Tipo_evidencia LIMIT 10;" 2>&1
```

### 5. Usuarios registrados (sin mostrar hashes)
```bash
psql -U postgres -d venom -c "SELECT nombre, email_usuario, rol, activo FROM tab_Usuarios;" 2>&1
```

## Reporte final
```
VENOM DB STATUS
════════════════════════════════
Conexión:    ✅/❌
Tablas:      N/12 encontradas
Triggers:    N triggers activos

Datos reales:
  tab_Usuarios:     N filas
  tab_Sesiones:     N filas
  tab_Artefactos:   N filas
  tab_Detecciones:  N filas
  tab_Scan_hosts:   N filas

Catálogos:
  tab_Protocolos:     N filas ✅/❌ vacío
  tab_Tipo_evidencia: N filas ✅/❌ vacío

Triggers auditoría: ✅/❌ (funcion_auditoria_y_triggers.sql)
════════════════════════════════
```

Si la BD no existe o no hay conexión, reportar claramente y mostrar cómo crearla:
```bash
# Crear BD desde cero:
psql -U postgres -c "CREATE DATABASE venom;"
psql -U postgres -d venom -f SQL/DB.sql
psql -U postgres -d venom -f SQL/funcion_auditoria_y_triggers.sql
```
