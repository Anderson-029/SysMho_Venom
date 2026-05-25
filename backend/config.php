<?php

// Cargar .env si está disponible
$env_file = __DIR__ . '/../.env';
if (file_exists($env_file)) {
    $lines = file($env_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        // Skip comments
        if (strpos(trim($line), '#') === 0) continue;

        // Parse KEY=VALUE
        if (strpos($line, '=') !== false) {
            list($key, $value) = explode('=', $line, 2);
            $key = trim($key);
            $value = trim($value);
            putenv("$key=$value");
        }
    }
}

// Configuración de PostgreSQL
$host = getenv('DB_HOST') ?: 'localhost';
$port = getenv('DB_PORT') ?: '5432';
$db   = strtolower(getenv('DB_NAME') ?: 'venom');
$user = getenv('DB_USER') ?: 'postgres';
$pass = getenv('DB_PASS') ?: '';

// Construir connection string
$connstr = "host=$host port=$port dbname=$db user=$user";
if ($pass !== '') {
    $connstr .= " password=$pass";
}

$conn = pg_connect($connstr);

if (!$conn) {
    error_log("PostgreSQL connection failed: " . pg_last_error());
    die(json_encode(['error' => 'No se pudo conectar a la base de datos', 'ok' => false]));
}

pg_set_client_encoding($conn, 'UTF8');
?>
