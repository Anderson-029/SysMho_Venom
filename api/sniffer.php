<?php
// POST /api/sniffer/start — iniciar captura
// POST /api/sniffer/stop  — detener captura
// Fase 2: ejecutará sniffer_engine.py via subprocess
require_once __DIR__ . '/middleware.php';
require_method('POST');

$path   = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$action = basename($path); // 'start' o 'stop'

if ($action === 'start') {
    $body = body_json();
    if (empty($body['iface'])) { json_err('iface requerido'); }
    // TODO Fase 2: lanzar sniffer_engine.iniciar_captura_sniffer()
    json_err('Bridge Python no implementado — pendiente Fase 2', 501);
}

if ($action === 'stop') {
    // TODO Fase 2: llamar sniffer_engine.detener_captura_sniffer()
    json_err('Bridge Python no implementado — pendiente Fase 2', 501);
}

json_err('Acción no reconocida', 404);
?>
