<?php
session_start();
require "config.php";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $email    = trim($_POST["email"]    ?? '');
    $password = trim($_POST["password"] ?? '');

    if ($email === '' || $password === '') {
        header("Location: ../landing/index.html?error=login");
        exit;
    }

    $stmt   = pg_prepare($conn, "login_query",
        "SELECT id_usuario, nombre, email_usuario, passwd_hash, rol, activo
         FROM tab_usuarios
         WHERE email_usuario = $1 AND rol = 'admin'
         LIMIT 1"
    );
    $result = pg_execute($conn, "login_query", [$email]);

    if ($result && pg_num_rows($result) === 1) {
        $user = pg_fetch_assoc($result);

        if ($user["activo"] !== "t") {
            header("Location: ../landing/index.html?error=usuario_inactivo");
            exit;
        }

        if (password_verify($password, $user["passwd_hash"])) {
            $_SESSION["user_id"]    = $user["id_usuario"];
            $_SESSION["user_name"]  = $user["nombre"];
            $_SESSION["user_role"]  = 'admin';
            $_SESSION["user_email"] = $user["email_usuario"];

            header("Location: ../admin-panel/admin.php");
            exit;
        }
    }

    header("Location: ../landing/index.html?error=login");
    exit;
}
?>
