#!/usr/bin/env python3
# =============================================================================
# Módulo      : db_bridge.py
# Descripción : Bridge entre el motor Python y PostgreSQL.
#               Responsabilidad única: persistir datos de sesión en la BD.
#               Si la BD no está disponible, falla silenciosamente (el motor
#               CLI sigue funcionando sin interrupción).
# =============================================================================

import os
import json
import hashlib
import datetime

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False

# ─── ID de sesión activa (compartido entre módulos vía este bridge) ───────────
_sesion_id: int | None = None
_conn = None


# ─── Conexión ─────────────────────────────────────────────────────────────────

def _get_conn():
    global _conn
    if _conn and not _conn.closed:
        return _conn
    if not _PSYCOPG2_AVAILABLE:
        return None
    try:
        _conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "VENOM"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", ""),
        )
        _conn.autocommit = True
        return _conn
    except Exception as e:
        print(f"[db_bridge] BD no disponible — continuando sin persistencia. ({e})")
        return None


# ─── Helpers internos ─────────────────────────────────────────────────────────

def _exec(sql: str, params: tuple = ()) -> "psycopg2.cursor | None":
    conn = _get_conn()
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur
    except Exception as e:
        print(f"[db_bridge] Error SQL: {e}")
        return None


def _get_or_create_alcance_cli() -> int | None:
    """Devuelve id del alcance 'CLI'. Si no existe y hay usuarios, lo crea."""
    cur = _exec("SELECT id_alcance FROM tab_alcances WHERE nombre = 'CLI' LIMIT 1")
    if cur is None:
        return None
    row = cur.fetchone()
    if row:
        return row[0]
    # Buscar cualquier usuario admin para asignarlo como creador
    cur2 = _exec("SELECT id_usuario FROM tab_usuarios WHERE rol = 'admin' LIMIT 1")
    if cur2 is None:
        return None
    admin = cur2.fetchone()
    if not admin:
        return None
    cur3 = _exec(
        """INSERT INTO tab_alcances
              (nombre, descripcion, creado_por, activo, usr_insert, fec_insert)
           VALUES (%s, %s, %s, true, 'venom_cli', NOW())
           RETURNING id_alcance""",
        ('CLI', 'Sesiones iniciadas desde línea de comandos', admin[0])
    )
    if cur3 is None:
        return None
    row = cur3.fetchone()
    return row[0] if row else None


def _get_or_create_runner_localhost() -> int | None:
    """Devuelve id del runner 'localhost'. Lo crea si no existe."""
    cur = _exec("SELECT id_runner FROM tab_runners WHERE mgmt_host = 'localhost' LIMIT 1")
    if cur is None:
        return None
    row = cur.fetchone()
    if row:
        return row[0]
    cur2 = _exec(
        """INSERT INTO tab_runners
              (nombre, mgmt_host, mgmt_ip, mgmt_interface, version_ag,
               estado, os_platform, capacidades, usr_insert, fec_insert)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'venom_cli', NOW())
           RETURNING id_runner""",
        ('localhost', 'localhost', '127.0.0.1', 'lo',
         '1.0', 'activo', 'Linux', ['mitm', 'sniffer', 'antisniff'])
    )
    if cur2 is None:
        return None
    row = cur2.fetchone()
    return row[0] if row else None


def _get_tipo_evidencia(codigo: str) -> int | None:
    cur = _exec(
        "SELECT id_evidencia FROM tab_tipo_evidencia WHERE codigo = %s LIMIT 1",
        (codigo,)
    )
    if cur is None:
        return None
    row = cur.fetchone()
    return row[0] if row else None


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ''


# ─── API pública ──────────────────────────────────────────────────────────────

def sesion_id() -> int | None:
    """Devuelve el id de sesión activa (None si no hay BD o no se registró)."""
    return _sesion_id


def registrar_sesion(
    victim: str,
    gateway: str,
    iface: str,
    forward: bool = False,
    masquerade: bool = False,
    antisniff: bool = False,
) -> int | None:
    """
    Inserta una nueva sesión MITM en tab_sesiones.
    Devuelve id_sesion o None si la BD no está disponible.
    """
    global _sesion_id

    id_alcance = _get_or_create_alcance_cli()
    id_runner  = _get_or_create_runner_localhost()

    if id_alcance is None or id_runner is None:
        print("[db_bridge] Sin alcance/runner — sesión no persiste en BD.")
        return None

    # Buscar id del usuario admin
    cur = _exec("SELECT id_usuario FROM tab_usuarios WHERE rol = 'admin' LIMIT 1")
    admin_id = cur.fetchone()[0] if cur and cur.fetchone() else None

    # fetchone consume el resultado, re-ejecutar
    cur2 = _exec("SELECT id_usuario FROM tab_usuarios WHERE rol = 'admin' LIMIT 1")
    if cur2 is None:
        return None
    row = cur2.fetchone()
    admin_id = row[0] if row else None

    cur3 = _exec(
        """INSERT INTO tab_sesiones
              (id_alcance, id_runner, creado_por, victima_ip, gateway_ip, interfaz,
               enable_forward, enable_masquerade, enable_antinsniff,
               estado, usr_insert, fec_insert)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ejecutandoce', 'venom_cli', NOW())
           RETURNING id_sesion""",
        (id_alcance, id_runner, admin_id, victim, gateway, iface,
         forward, masquerade, antisniff)
    )
    if cur3 is None:
        return None
    row = cur3.fetchone()
    if row:
        _sesion_id = row[0]
        print(f"[db_bridge] Sesión registrada en BD — id_sesion={_sesion_id}")
        registrar_evento('SESION_INICIO', f'MITM iniciado: víctima={victim} gateway={gateway}')
    return _sesion_id


def actualizar_sesion(estado: str) -> None:
    """Actualiza el estado de la sesión activa (terminada/fallida)."""
    if _sesion_id is None:
        return
    estados_validos = {'ejecutandoce', 'terminada', 'pendiente', 'fallida'}
    if estado not in estados_validos:
        return
    fin_sql = "NOW()" if estado in ('terminada', 'fallida') else "NULL"
    _exec(
        f"""UPDATE tab_sesiones
            SET estado = %s,
                fin = {fin_sql},
                usr_update = 'venom_cli',
                fec_update = NOW()
            WHERE id_sesion = %s""",
        (estado, _sesion_id)
    )
    registrar_evento('SESION_FIN', f'Estado final: {estado}')


def registrar_artefacto(ruta: str, tipo_codigo: str = 'pcap') -> None:
    """
    Registra un artefacto (pcap, txt, sha256) en tab_artefactos.
    Calcula SHA-256 del archivo automáticamente.
    """
    if _sesion_id is None or not os.path.isfile(ruta):
        return

    id_tipo = _get_tipo_evidencia(tipo_codigo)
    if id_tipo is None:
        return

    sha = _sha256_file(ruta)
    tamano = os.path.getsize(ruta)

    _exec(
        """INSERT INTO tab_artefactos
              (id_sesion, id_evidencia, ruta_archivo, sha256, tamano_bytes,
               usr_insert, fec_insert)
           VALUES (%s, %s, %s, %s, %s, 'venom_cli', NOW())
           ON CONFLICT (id_sesion, id_evidencia) DO NOTHING""",
        (_sesion_id, id_tipo, os.path.abspath(ruta), sha, tamano)
    )


def registrar_deteccion(ip: str, mac: str, severidad: int = 3) -> None:
    """Registra un sniffer detectado en tab_detecciones."""
    if _sesion_id is None:
        return
    detalles = json.dumps({'metodo': 'arp_fake', 'ip': ip, 'mac': mac})
    _exec(
        """INSERT INTO tab_detecciones
              (id_sesion, ip_sospechosa, mac_sospechosa, severidad, detalles,
               usr_insert, fec_insert)
           VALUES (%s, %s, %s, %s, %s::jsonb, 'venom_cli', NOW())
           ON CONFLICT (id_sesion, ip_sospechosa, mac_sospechosa, detectado_en)
           DO NOTHING""",
        (_sesion_id, ip, mac, severidad, detalles)
    )


def registrar_scan_hosts(hosts: list[tuple]) -> None:
    """
    Registra hosts descubiertos por escaneo ARP en tab_scan_hosts.
    hosts = [(ip, mac, vendor), ...]
    """
    if _sesion_id is None or not hosts:
        return
    for ip, mac, vendor in hosts:
        _exec(
            """INSERT INTO tab_scan_hosts
                  (id_sesion, ip, mac, vendor, usr_insert, fec_insert)
               VALUES (%s, %s, %s, %s, 'venom_cli', NOW())
               ON CONFLICT (id_sesion, ip) DO NOTHING""",
            (_sesion_id, ip, mac or None, vendor or None)
        )


def registrar_evento(codigo: str, mensaje: str, nivel: str = 'info',
                     payload: dict | None = None) -> None:
    """Registra un evento en tab_eventos_sesion."""
    if _sesion_id is None:
        return
    _exec(
        """INSERT INTO tab_eventos_sesion
              (id_sesion, codigo, nivel, mensaje, payload, usr_insert, fec_insert)
           VALUES (%s, %s, %s, %s, %s::jsonb, 'venom_cli', NOW())
           ON CONFLICT DO NOTHING""",
        (_sesion_id, codigo, nivel, mensaje,
         json.dumps(payload) if payload else None)
    )


def registrar_stats(stats: dict) -> None:
    """
    Registra estadísticas de captura por protocolo.
    stats = {'DNS': 120, 'HTTP': 45, ...}
    """
    if _sesion_id is None or not stats:
        return
    for protocolo, paquetes in stats.items():
        cur = _exec(
            "SELECT code FROM tab_protocolos WHERE nombre = %s LIMIT 1",
            (protocolo,)
        )
        if cur is None:
            continue
        row = cur.fetchone()
        if not row:
            continue
        proto_code = row[0]
        _exec(
            """INSERT INTO tab_stats_protocolo
                  (id_sesion, protocolo_code, paquetes, usr_insert, fec_insert)
               VALUES (%s, %s, %s, 'venom_cli', NOW())
               ON CONFLICT DO NOTHING""",
            (_sesion_id, proto_code, paquetes)
        )
