<?php
// Router principal para /api/
// Despacha según el path de la URL

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
// Normalizar: /api/sessions → sessions
$segment = trim(str_replace('/api', '', $path), '/');
$parts   = explode('/', $segment);
$route   = $parts[0] ?? '';

// Añadir id a GET si viene en la URL: /api/sessions/123
if (isset($parts[1]) && $parts[1] !== '') {
    $_GET['id'] = $parts[1];
}

switch ($route) {
    case 'sessions':
        require __DIR__ . '/sessions.php';
        break;
    case 'stats':
        require __DIR__ . '/stats.php';
        break;
    case 'logs':
        // Distinguir entre list, download y hash por query param action
        if (!isset($_GET['action'])) {
            $_GET['action'] = 'list';
        }
        require __DIR__ . '/logs.php';
        break;
    case 'antisniffer':
        require __DIR__ . '/antisniffer.php';
        break;
    case 'audit':
        require __DIR__ . '/audit.php';
        break;
    case 'reports':
        require __DIR__ . '/reports.php';
        break;
    case 'users':
        // Pasar path info para que users.php detecte /{id}
        $_SERVER['PATH_INFO'] = '/' . implode('/', array_slice($parts, 0));
        require __DIR__ . '/users.php';
        break;
    case 'stream':
        require __DIR__ . '/stream.php';
        break;
    case 'network':
        require __DIR__ . '/network.php';
        break;
    case 'arp':
        require __DIR__ . '/arp.php';
        break;
    case 'sniffer':
        require __DIR__ . '/sniffer.php';
        break;
    default:
        http_response_code(404);
        header('Content-Type: application/json');
        echo json_encode(['ok' => false, 'error' => "Endpoint /$route no existe"]);
        break;
}
?>
