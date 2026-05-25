<?php
require_once __DIR__ . '/middleware.php';
require_method('GET');

// Trail de auditoría desde tab_eventos_sesion
$where  = ['e.fec_delete IS NULL'];
$params = [];
$i      = 1;

if (!empty($_GET['from'])) {
    $where[] = "e.inicio >= $" . $i++;
    $params[] = $_GET['from'];
}
if (!empty($_GET['to'])) {
    $where[] = "e.inicio <= $" . $i++ . "::date + interval '1 day'";
    $params[] = $_GET['to'];
}

$sql    = "SELECT e.id_evento, e.id_sesion, e.tipo_evento, e.descripcion,
                  e.inicio AS ts, e.datos_extra,
                  u.nombre AS usuario
           FROM tab_eventos_sesion e
           LEFT JOIN tab_sesiones s ON s.id_sesion = e.id_sesion
           LEFT JOIN tab_usuarios u ON u.id_usuario = s.creado_por
           WHERE " . implode(' AND ', $where) . "
           ORDER BY e.inicio DESC
           LIMIT 500";

$stmt   = pg_prepare($conn, 'audit_list', $sql);
$result = pg_execute($conn, 'audit_list', $params);
$rows   = pg_fetch_all($result) ?: [];

json_ok(array_map(fn($r) => [
    'ts'     => $r['ts'],
    'user'   => $r['usuario'] ?? 'system',
    'action' => $r['tipo_evento'],
    'detail' => $r['descripcion'],
], $rows));
?>
