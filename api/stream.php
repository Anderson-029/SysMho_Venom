<?php
// SSE endpoint — emite eventos en tiempo real desde la BD
// Tipos de evento: session_update | detection | keepalive

session_start();
if (!isset($_SESSION['user_id']) || $_SESSION['user_role'] !== 'admin') {
    http_response_code(401);
    exit;
}
session_write_close(); // liberar el bloqueo de sesión para no bloquear otras peticiones

require_once __DIR__ . '/../backend/config.php';

// Cabeceras SSE
header('Content-Type: text/event-stream; charset=utf-8');
header('Cache-Control: no-cache');
header('X-Accel-Buffering: no');   // deshabilitar buffer en nginx
header('Connection: keep-alive');

// Punto de partida: el cliente envía Last-Event-ID con el último id_evento conocido
$last_event_id  = (int)($_SERVER['HTTP_LAST_EVENT_ID'] ?? 0);
$last_detect_id = 0;
$last_session_check = date('Y-m-d H:i:s', strtotime('-5 seconds'));

set_time_limit(0);
ignore_user_abort(false);

function sse(string $type, array $data, int $id = 0): void {
    if ($id > 0) echo "id: $id\n";
    echo "event: $type\n";
    echo 'data: ' . json_encode($data) . "\n\n";
    if (ob_get_level() > 0) ob_flush();
    flush();
}

function sse_keepalive(): void {
    echo ": keepalive " . date('H:i:s') . "\n\n";
    if (ob_get_level() > 0) ob_flush();
    flush();
}

$tick = 0;

while (!connection_aborted()) {
    $tick++;

    // ── Nuevos eventos de sesión ────────────────────────────────
    $res = pg_query_params($conn,
        "SELECT id_evento, codigo, nivel, mensaje, payload, fec_insert
           FROM tab_eventos_sesion
          WHERE id_evento > $1
          ORDER BY id_evento ASC
          LIMIT 20",
        [$last_event_id]
    );
    if ($res) {
        while ($row = pg_fetch_assoc($res)) {
            $last_event_id = (int)$row['id_evento'];
            sse('session_event', [
                'id'      => $last_event_id,
                'code'    => $row['codigo'],
                'level'   => $row['nivel'],
                'msg'     => $row['mensaje'],
                'payload' => $row['payload'] ? json_decode($row['payload'], true) : null,
                'ts'      => $row['fec_insert'],
            ], $last_event_id);
        }
    }

    // ── Nuevas detecciones anti-sniffer ────────────────────────
    $res2 = pg_query_params($conn,
        "SELECT id_deteccion, ip_sospechosa, mac_sospechosa, severidad, detectado_en
           FROM tab_detecciones
          WHERE id_deteccion > $1
          ORDER BY id_deteccion ASC
          LIMIT 10",
        [$last_detect_id]
    );
    if ($res2) {
        while ($row = pg_fetch_assoc($res2)) {
            $last_detect_id = (int)$row['id_deteccion'];
            sse('detection', [
                'id'       => $last_detect_id,
                'ip'       => $row['ip_sospechosa'],
                'mac'      => $row['mac_sospechosa'],
                'severity' => (int)$row['severidad'],
                'ts'       => $row['detectado_en'],
            ]);
        }
    }

    // ── Estado de sesiones activas (cada 5 ticks = ~15s) ───────
    if ($tick % 5 === 0) {
        $res3 = pg_query($conn,
            "SELECT COUNT(*) AS n FROM tab_sesiones
              WHERE estado = 'ejecutandoce' AND fec_delete IS NULL"
        );
        $active = $res3 ? (int)(pg_fetch_assoc($res3)['n'] ?? 0) : 0;
        sse('session_status', ['active_count' => $active]);
    }

    // ── Keepalive cada 15 ticks (~45s) ─────────────────────────
    if ($tick % 15 === 0) {
        sse_keepalive();
    }

    sleep(3);
}
?>
