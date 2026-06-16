<?php
// api/categorias/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();

$sql = "SELECT c.*, (SELECT COUNT(*) FROM productos p WHERE p.categoria_id = c.id AND p.estado != 'inactivo') as total_productos FROM categorias c WHERE c.estado = 'activo' ORDER BY c.orden ASC";
$stmt = $db->prepare($sql);
$stmt->execute();
$categorias = $stmt->fetchAll();

respondSuccess(['data' => $categorias]);