# AGENTS.md — SQL/ (Schema y Auditoría PostgreSQL)

## Responsabilidad

Define la estructura de datos en la base de datos `VENOM` en PostgreSQL, garantizando la integridad referencial, el registro automático de logs, y auditoría mediante triggers.

---

## Archivos

| Archivo | Estado | Contenido |
|---------|--------|-----------|
| `DB.sql` | Completo | Contiene el schema DDL de las tablas, índices principales y la población inicial de catálogos (`tab_Protocolos` y `tab_Tipo_evidencia`). Restringe los roles a `'admin'`. |
| `funcion_auditoria_y_triggers.sql` | **COMPLETO** | Función `fn_audit_update()` y 12 triggers `BEFORE UPDATE` que actualizan automáticamente `fec_update` y `usr_update` al modificar registros. |

---

## Restricciones de Acceso (Single Admin)

Para cumplir con el diseño de Administrador Único, las tablas relacionadas con usuarios restringen los roles permitidos mediante constraints:
- `tab_Usuarios`: `rol VARCHAR NOT NULL CHECK (rol IN ('admin'))`
- `tokens_invitacion`: `rol_destino VARCHAR NOT NULL CHECK (rol_destino IN ('admin'))`

---

## Columnas de Auditoría

Todas las tablas cuentan con las siguientes columnas estándar de auditoría:
- `usr_insert` (usuario de inserción)
- `fec_insert` (fecha/hora de inserción, por defecto `NOW()`)
- `usr_update` (usuario de última actualización)
- `fec_update` (fecha/hora de última actualización)
- `usr_delete` (usuario de eliminación lógica)
- `fec_delete` (fecha/hora de eliminación lógica)

**Regla de Negocio:** No se realiza borrado físico (`DELETE`). Se utiliza borrado lógico completando las columnas `usr_delete` y `fec_delete`.

---

## Triggers Implementados

El script `funcion_auditoria_y_triggers.sql` crea la función de auditoría:
```sql
CREATE OR REPLACE FUNCTION fn_audit_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fec_update = NOW();
    NEW.usr_update = current_user;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
Y asocia un trigger `BEFORE UPDATE` a las 12 tablas principales para registrar automáticamente el usuario de PostgreSQL y la marca de tiempo de la actualización.

---

## Validación y Despliegue

```bash
# Crear base de datos
psql -U postgres -c "CREATE DATABASE venom;"

# Aplicar schema y triggers
psql -U postgres -d venom -f SQL/DB.sql
psql -U postgres -d venom -f SQL/funcion_auditoria_y_triggers.sql
```
