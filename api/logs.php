<?php
require_once __DIR__ . '/middleware.php';

$method = $_SERVER['REQUEST_METHOD'];

// GET /api/logs/list  → lista de artefactos desde BD
// GET /api/logs/download?path= → descarga archivo
// GET /api/logs/hash?path=     → contenido del .sha256

$action = $_GET['action'] ?? 'list';

if ($method === 'GET' && $action === 'download') {
    $path = $_GET['path'] ?? '';
    $base = realpath(__DIR__ . '/../');

    // Restringir al directorio del proyecto
    $real = realpath($path);
    if (!$real || strpos($real, $base) !== 0 || !file_exists($real)) {
        json_err('Archivo no encontrado', 404);
    }

    $ext  = strtolower(pathinfo($real, PATHINFO_EXTENSION));
    $mime = $ext === 'pcap' ? 'application/vnd.tcpdump.pcap' : 'text/plain';

    header('Content-Type: ' . $mime);
    header('Content-Disposition: attachment; filename="' . basename($real) . '"');
    header('Content-Length: ' . filesize($real));
    readfile($real);
    exit;
}

if ($method === 'GET' && $action === 'hash') {
    $path = $_GET['path'] ?? '';
    $base = realpath(__DIR__ . '/../');
    $real = realpath($path);
    if (!$real || strpos($real, $base) !== 0 || !file_exists($real)) {
        json_err('Hash no encontrado', 404);
    }
    json_ok(['hash' => trim(file_get_contents($real))]);
}

// GET /api/logs/list → artefactos desde BD con filtros
if ($method === 'GET') {
    $where  = ['a.fec_delete IS NULL'];
    $params = [];
    $i      = 1;

    if (!empty($_GET['protocol'])) {
        $where[] = "p.nombre ILIKE $" . $i++;
        $params[] = $_GET['protocol'];
    }
    if (!empty($_GET['date'])) {
        $where[] = "a.creado_en::date = $" . $i++;
        $params[] = $_GET['date'];
    }
    if (!empty($_GET['session'])) {
        $where[] = "a.id_sesion = $" . $i++;
        $params[] = $_GET['session'];
    }

    $sql = "SELECT a.id_artefacto, a.id_sesion, a.ruta_archivo, a.sha256,
                   a.tamano_bytes, a.creado_en,
                   te.codigo AS tipo, te.nombre AS tipo_nombre,
                   te.mime_type
            FROM tab_artefactos a
            JOIN tab_tipo_evidencia te ON te.id_evidencia = a.id_evidencia
            WHERE " . implode(' AND ', $where) . "
            ORDER BY a.creado_en DESC
            LIMIT 500";

    $stmt   = pg_prepare($conn, 'logs_list', $sql);
    $result = pg_execute($conn, 'logs_list', $params);
    $rows   = pg_fetch_all($result) ?: [];
    json_ok($rows);
}

json_err('Método no permitido', 405);
?>
