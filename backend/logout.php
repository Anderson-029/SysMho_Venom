<?php
session_start();

// Borrar todas las variables de sesión
$_SESSION = [];

// Destruir la sesión
session_unset();
session_destroy();

// Redirigir al login
header("Location: ../landing/index.html?msg=logout");
exit;
?>
