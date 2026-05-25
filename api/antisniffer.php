<?php
require_once __DIR__ . '/middleware.php';
require_method('GET');

$where  = ['fec_delete IS NULL'];
$params = [];
$i      = 1;

if (!empty($_GET['session'])) {
    $where[] = "id_sesion = $" . $i++;
    $params[] = $_GET['session'];
}

$sql    = "SELECT id_deteccion, id_sesion, ip_sospechosa, mac_sospechosa,
                  severidad, detalles, detectado_en
           FROM tab_detecciones
           WHERE " . implode(' AND ', $where) . "
           ORDER BY detectado_en DESC
           LIMIT 200";

$stmt   = pg_prepare($conn, 'antisniff_list', $sql);
$result = pg_execute($conn, 'antisniff_list', $params);
$rows   = pg_fetch_all($result) ?: [];

json_ok($rows);
?>
