<?php
require_once __DIR__ . '/middleware.php';
require_method('GET');

$sesiones_activas = pg_fetch_assoc(pg_query($conn,
    "SELECT COUNT(*) AS n FROM tab_sesiones WHERE estado = 'ejecutandoce' AND fec_delete IS NULL"
))['n'] ?? 0;

$total_artefactos = pg_fetch_assoc(pg_query($conn,
    "SELECT COUNT(*) AS n FROM tab_artefactos WHERE fec_delete IS NULL"
))['n'] ?? 0;

$total_detecciones = pg_fetch_assoc(pg_query($conn,
    "SELECT COUNT(*) AS n FROM tab_detecciones WHERE fec_delete IS NULL"
))['n'] ?? 0;

$total_hosts = pg_fetch_assoc(pg_query($conn,
    "SELECT COUNT(*) AS n FROM tab_scan_hosts WHERE fec_delete IS NULL"
))['n'] ?? 0;

$total_protocolos = pg_fetch_assoc(pg_query($conn,
    "SELECT COUNT(DISTINCT protocolo_code) AS n FROM tab_stats_protocolo"
))['n'] ?? 0;

json_ok([
    'sesiones_activas'  => (int)$sesiones_activas,
    'total_artefactos'  => (int)$total_artefactos,
    'total_detecciones' => (int)$total_detecciones,
    'hosts_descubiertos'=> (int)$total_hosts,
    'protocolos'        => (int)$total_protocolos,
]);
?>
