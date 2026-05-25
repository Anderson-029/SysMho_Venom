<?php
// POST /api/network/scan — escaneo ARP de la red local
// Fase 2: ejecutará python3 code/venom_route.py en modo escaneo
require_once __DIR__ . '/middleware.php';
require_method('POST');

$body = body_json();
if (empty($body['interface'])) { json_err('interface requerido'); }
if (empty($body['cidr']))      { json_err('cidr requerido'); }

// TODO Fase 2: ejecutar network_utils.escaneo_red() via subprocess Python
// Por ahora responde que el bridge no está implementado aún
json_err('Bridge Python no implementado — pendiente Fase 2', 501);
?>
