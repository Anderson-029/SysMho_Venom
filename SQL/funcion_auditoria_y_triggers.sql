-- ============================================================
-- SysMho Venom — Función de auditoría y triggers
-- Aplica automáticamente fec_update y usr_update en UPDATE
-- ============================================================

-- Función genérica: actualiza fec_update y usr_update en cada UPDATE
CREATE OR REPLACE FUNCTION fn_audit_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fec_update = NOW();
    NEW.usr_update = current_user;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- Triggers por tabla
-- ============================================================

CREATE TRIGGER trg_audit_usuarios
BEFORE UPDATE ON tab_Usuarios
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_tokens_invitacion
BEFORE UPDATE ON tokens_invitacion
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_alcances
BEFORE UPDATE ON tab_Alcances
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_runners
BEFORE UPDATE ON tab_Runners
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_sesiones
BEFORE UPDATE ON tab_Sesiones
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_tipo_evidencia
BEFORE UPDATE ON tab_Tipo_evidencia
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_protocolos
BEFORE UPDATE ON tab_Protocolos
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_artefactos
BEFORE UPDATE ON tab_Artefactos
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_detecciones
BEFORE UPDATE ON tab_Detecciones
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_stats_protocolo
BEFORE UPDATE ON tab_Stats_protocolo
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_eventos_sesion
BEFORE UPDATE ON tab_Eventos_sesion
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();

CREATE TRIGGER trg_audit_scan_hosts
BEFORE UPDATE ON tab_Scan_hosts
FOR EACH ROW EXECUTE FUNCTION fn_audit_update();
