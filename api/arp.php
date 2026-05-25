<?php
// POST /api/arp/start   — iniciar ARP spoofing (MITM)
// POST /api/arp/restore — restaurar tablas ARP
// Fase 2: ejecutará venom_route.py via subprocess
require_once __DIR__ . '/middleware.php';
require_method('POST');

$path   = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$action = basename($path); // 'start' o 'restore'

if ($action === 'start') {
    $body = body_json();
    $required = ['victim', 'gateway', 'iface'];
    foreach ($required as $f) {
        if (empty($body[$f])) { json_err("Campo requerido: $f"); }
    }
    // TODO Fase 2: lanzar venom_route.py con los parámetros
    json_err('Bridge Python no implementado — pendiente Fase 2', 501);
}

if ($action === 'restore') {
    // TODO Fase 2: enviar señal de stop al proceso venom_route
    json_err('Bridge Python no implementado — pendiente Fase 2', 501);
}

json_err('Acción no reconocida', 404);
?>
