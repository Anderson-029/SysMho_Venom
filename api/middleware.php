<?php
// Middleware compartido para todos los endpoints /api/
// Verifica sesión admin, setea headers JSON y maneja CORS

session_start();
require_once __DIR__ . '/../backend/config.php';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

// Solo peticiones desde el mismo origen
if (!isset($_SESSION['user_id']) || $_SESSION['user_role'] !== 'admin') {
    http_response_code(401);
    echo json_encode(['ok' => false, 'error' => 'No autorizado']);
    exit;
}

function json_ok($data) {
    echo json_encode(['ok' => true, 'data' => $data]);
    exit;
}

function json_err($msg, $code = 400) {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $msg]);
    exit;
}

function require_method($method) {
    if ($_SERVER['REQUEST_METHOD'] !== strtoupper($method)) {
        json_err('Método no permitido', 405);
    }
}

function body_json() {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    if ($data === null && $raw !== '') {
        json_err('Body JSON inválido');
    }
    return $data ?? [];
}
?>
