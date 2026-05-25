<?php
require_once __DIR__ . '/middleware.php';
require_method('POST');

$body  = body_json();
$dates  = trim($body['dates']  ?? '');
$format = trim($body['format'] ?? 'Markdown');

if ($dates === '') { json_err('Rango de fechas requerido'); }

// Construir reporte básico en texto/markdown con datos de la BD
$sesiones = pg_fetch_all(pg_query($conn,
    "SELECT id_sesion, victima_ip, gateway_ip, interfaz, estado, inicio, fin
     FROM tab_sesiones WHERE fec_delete IS NULL ORDER BY inicio DESC LIMIT 50"
)) ?: [];

$artefactos = pg_fetch_all(pg_query($conn,
    "SELECT a.ruta_archivo, te.codigo AS tipo, a.sha256, a.creado_en
     FROM tab_artefactos a
     JOIN tab_tipo_evidencia te ON te.id_evidencia = a.id_evidencia
     WHERE a.fec_delete IS NULL ORDER BY a.creado_en DESC LIMIT 100"
)) ?: [];

$detecciones = pg_fetch_all(pg_query($conn,
    "SELECT ip_sospechosa, mac_sospechosa, severidad, detectado_en
     FROM tab_detecciones WHERE fec_delete IS NULL ORDER BY detectado_en DESC LIMIT 50"
)) ?: [];

$now = date('Y-m-d H:i:s');

$md  = "# Reporte VENOM-ROUTE\n";
$md .= "**Generado:** $now  \n";
$md .= "**Rango:** $dates  \n\n";

$md .= "---\n## Sesiones MITM (" . count($sesiones) . ")\n\n";
$md .= "| ID | Víctima | Gateway | Interfaz | Estado | Inicio | Fin |\n";
$md .= "|----|---------|---------|----------|--------|--------|-----|\n";
foreach ($sesiones as $s) {
    $md .= "| {$s['id_sesion']} | {$s['victima_ip']} | {$s['gateway_ip']} | {$s['interfaz']} | {$s['estado']} | {$s['inicio']} | {$s['fin']} |\n";
}

$md .= "\n---\n## Artefactos capturados (" . count($artefactos) . ")\n\n";
$md .= "| Archivo | Tipo | SHA-256 | Fecha |\n";
$md .= "|---------|------|---------|-------|\n";
foreach ($artefactos as $a) {
    $file = basename($a['ruta_archivo']);
    $sha  = substr($a['sha256'] ?? '', 0, 16) . '…';
    $md  .= "| $file | {$a['tipo']} | $sha | {$a['creado_en']} |\n";
}

$md .= "\n---\n## Detecciones Anti-Sniffer (" . count($detecciones) . ")\n\n";
$md .= "| IP | MAC | Severidad | Detectado en |\n";
$md .= "|----|-----|-----------|-------------|\n";
foreach ($detecciones as $d) {
    $md .= "| {$d['ip_sospechosa']} | {$d['mac_sospechosa']} | {$d['severidad']} | {$d['detectado_en']} |\n";
}

$md .= "\n---\n*Reporte generado por SysMho Venom — uso en redes autorizadas.*\n";

// Por ahora siempre devuelve Markdown (PDF/CSV en fases futuras)
header('Content-Type: text/markdown; charset=utf-8');
header('Content-Disposition: attachment; filename="venom_report_' . date('Ymd_His') . '.md"');
echo $md;
exit;
?>
