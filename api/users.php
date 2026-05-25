<?php
require_once __DIR__ . '/middleware.php';

$method = $_SERVER['REQUEST_METHOD'];

// GET /api/users — lista de usuarios
if ($method === 'GET') {
    // GET /api/users/{id}
    $parts = explode('/', trim($_SERVER['PATH_INFO'] ?? '', '/'));
    $uid = $parts[1] ?? null;

    if ($uid) {
        $stmt = pg_prepare($conn, 'get_user',
            "SELECT id_usuario, nombre, email_usuario, rol, activo, fec_insert
               FROM tab_usuarios WHERE id_usuario = $1 AND fec_delete IS NULL");
        $res = pg_execute($conn, 'get_user', [$uid]);
        $row = pg_fetch_assoc($res);
        if (!$row) json_err('Usuario no encontrado', 404);
        json_ok($row);
    }

    $res = pg_query($conn,
        "SELECT id_usuario, nombre, email_usuario, rol, activo, fec_insert
           FROM tab_usuarios WHERE fec_delete IS NULL ORDER BY fec_insert DESC");
    json_ok(pg_fetch_all($res) ?: []);
}

// POST /api/users — crear usuario
if ($method === 'POST') {
    $body = body_json();
    $name  = trim($body['name']  ?? '');
    $email = trim($body['email'] ?? '');
    $pass  = trim($body['password'] ?? bin2hex(random_bytes(8)));

    if (!$name || !$email) json_err('name y email son obligatorios');
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) json_err('Email inválido');

    $hash = password_hash($pass, PASSWORD_BCRYPT);
    $stmt = pg_prepare($conn, 'ins_user',
        "INSERT INTO tab_usuarios (nombre, email_usuario, passwd_hash, rol, activo, usr_insert, fec_insert)
              VALUES ($1, $2, $3, 'admin', true, 'admin_panel', NOW())
         RETURNING id_usuario");
    $res = pg_execute($conn, 'ins_user', [$name, $email, $hash]);
    if (!$res) json_err('Error creando usuario: ' . pg_last_error($conn), 500);
    $row = pg_fetch_assoc($res);
    json_ok(['id_usuario' => $row['id_usuario'], 'password_generada' => $pass]);
}

// PUT /api/users/{id} — toggle activo
if ($method === 'PUT') {
    $parts = explode('/', trim($_SERVER['PATH_INFO'] ?? '', '/'));
    $uid = $parts[1] ?? null;
    if (!$uid) json_err('ID requerido');

    $stmt = pg_prepare($conn, 'toggle_user',
        "UPDATE tab_usuarios SET activo = NOT activo, usr_update = 'admin_panel', fec_update = NOW()
          WHERE id_usuario = $1 AND fec_delete IS NULL RETURNING activo");
    $res = pg_execute($conn, 'toggle_user', [$uid]);
    if (!$res || pg_num_rows($res) === 0) json_err('Usuario no encontrado', 404);
    $row = pg_fetch_assoc($res);
    json_ok(['activo' => $row['activo'] === 't']);
}

// DELETE /api/users/{id} — soft delete
if ($method === 'DELETE') {
    $parts = explode('/', trim($_SERVER['PATH_INFO'] ?? '', '/'));
    $uid = $parts[1] ?? null;
    if (!$uid) json_err('ID requerido');

    $stmt = pg_prepare($conn, 'del_user',
        "UPDATE tab_usuarios SET fec_delete = NOW(), usr_delete = 'admin_panel'
          WHERE id_usuario = $1 AND fec_delete IS NULL");
    $res = pg_execute($conn, 'del_user', [$uid]);
    if (!$res) json_err('Error eliminando usuario', 500);
    json_ok(['deleted' => pg_affected_rows($res) > 0]);
}

json_err('Método no permitido', 405);
?>
