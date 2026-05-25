<?php
require_once __DIR__ . '/middleware.php';

$method = $_SERVER['REQUEST_METHOD'];

// GET /api/sessions        → lista
// GET /api/sessions?id=X  → detalle por id
if ($method === 'GET') {
    $id = $_GET['id'] ?? null;

    if ($id !== null) {
        // Detalle de una sesión
        $stmt   = pg_prepare($conn, 'sess_by_id',
            "SELECT s.id_sesion, s.victima_ip, s.gateway_ip, s.interfaz,
                    s.enable_forward, s.enable_masquerade, s.enable_antinsniff,
                    s.estado, s.inicio, s.fin, s.notas,
                    a.nombre AS alcance, r.nombre AS runner
             FROM tab_sesiones s
             LEFT JOIN tab_alcances a ON a.id_alcance = s.id_alcance
             LEFT JOIN tab_runners  r ON r.id_runner  = s.id_runner
             WHERE s.id_sesion = $1 AND s.fec_delete IS NULL"
        );
        $result = pg_execute($conn, 'sess_by_id', [$id]);
        $row    = pg_fetch_assoc($result);
        if (!$row) { json_err('Sesión no encontrada', 404); }
        json_ok($row);
    }

    // Lista con filtros opcionales
    $where  = ["s.fec_delete IS NULL"];
    $params = [];
    $i      = 1;

    if (!empty($_GET['estado'])) {
        $where[] = "s.estado = $" . $i++;
        $params[] = $_GET['estado'];
    }
    if (!empty($_GET['iface'])) {
        $where[] = "s.interfaz ILIKE $" . $i++;
        $params[] = '%' . $_GET['iface'] . '%';
    }
    if (!empty($_GET['fecha'])) {
        $where[] = "s.inicio::date = $" . $i++;
        $params[] = $_GET['fecha'];
    }

    $sql = "SELECT s.id_sesion, s.victima_ip, s.gateway_ip, s.interfaz,
                   s.enable_forward AS \"F\", s.enable_masquerade AS \"M\",
                   s.enable_antinsniff AS \"A\", s.estado, s.inicio, s.fin
            FROM tab_sesiones s
            WHERE " . implode(' AND ', $where) . "
            ORDER BY s.inicio DESC
            LIMIT 200";

    $stmt   = pg_prepare($conn, 'sess_list', $sql);
    $result = pg_execute($conn, 'sess_list', $params);
    $rows   = pg_fetch_all($result) ?: [];
    json_ok($rows);
}

// POST /api/sessions → crear sesión (inicia registro, el motor Python corre aparte)
if ($method === 'POST') {
    $body = body_json();
    $required = ['id_alcance','id_runner','victima_ip','gateway_ip','interfaz'];
    foreach ($required as $f) {
        if (empty($body[$f])) { json_err("Campo requerido: $f"); }
    }

    $stmt = pg_prepare($conn, 'sess_create',
        "INSERT INTO tab_sesiones
            (id_alcance, id_runner, creado_por, victima_ip, gateway_ip, interfaz,
             enable_forward, enable_masquerade, enable_antinsniff, estado,
             usr_insert, fec_insert)
         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,'pendiente',current_user,NOW())
         RETURNING id_sesion"
    );
    $result = pg_execute($conn, 'sess_create', [
        $body['id_alcance'],
        $body['id_runner'],
        $_SESSION['user_id'],
        $body['victima_ip'],
        $body['gateway_ip'],
        $body['interfaz'],
        isset($body['forward'])    ? 'true' : 'false',
        isset($body['masquerade']) ? 'true' : 'false',
        isset($body['antisniff'])  ? 'true' : 'false',
    ]);
    $row = pg_fetch_assoc($result);
    http_response_code(201);
    json_ok(['id_sesion' => $row['id_sesion']]);
}

// PATCH /api/sessions?id=X → actualizar estado
if ($method === 'PATCH') {
    $id   = $_GET['id'] ?? null;
    if (!$id) { json_err('id requerido'); }
    $body = body_json();

    $estados_validos = ['ejecutandoce','terminada','pendiente','fallida'];
    if (!in_array($body['estado'] ?? '', $estados_validos)) {
        json_err('Estado inválido');
    }

    $stmt = pg_prepare($conn, 'sess_patch',
        "UPDATE tab_sesiones
         SET estado = $1, fin = CASE WHEN $1 IN ('terminada','fallida') THEN NOW() ELSE fin END,
             usr_update = current_user, fec_update = NOW()
         WHERE id_sesion = $2 AND fec_delete IS NULL"
    );
    pg_execute($conn, 'sess_patch', [$body['estado'], $id]);
    json_ok(['updated' => true]);
}

json_err('Método no permitido', 405);
?>
