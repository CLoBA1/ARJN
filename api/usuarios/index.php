<?php
// api/usuarios/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();
$stmt = $db->prepare("SELECT id, nombre, username, rol, estado, avatar, ultimo_acceso, created_at, updated_at FROM usuarios WHERE estado != 'eliminado'");
$stmt->execute();
$usuarios = $stmt->fetchAll();

respondSuccess(['data' => $usuarios]);