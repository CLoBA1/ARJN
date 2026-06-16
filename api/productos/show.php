<?php
// api/productos/show.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$db = (new Database())->getConnection();

$stmt = $db->prepare("SELECT * FROM v_productos_completos WHERE id = ?");
$stmt->execute([$_GET['id']]);
$producto = $stmt->fetch();

if (!$producto) respondError('Producto no encontrado', 404);

$stmtMov = $db->prepare("SELECT * FROM v_movimientos_completos WHERE producto_id = ? ORDER BY created_at DESC LIMIT 5");
$stmtMov->execute([$_GET['id']]);
$movimientos = $stmtMov->fetchAll();

$producto['movimientos'] = $movimientos;

respondSuccess($producto);