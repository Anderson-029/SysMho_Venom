<?php
session_start();

// Verificar sesión activa y rol admin
if (!isset($_SESSION["user_id"]) || $_SESSION["user_role"] !== 'admin') {
    header("Location: ../landing/index.html?error=acceso_denegado");
    exit;
}
?>
