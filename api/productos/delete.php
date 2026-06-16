<?php
// api/productos/delete.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'DELETE') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$db = (new Database())->getConnection();

// Soft delete
$stmt = $db->prepare("UPDATE productos SET estado = 'inactivo' WHERE id = ?");
$stmt->execute([$_GET['id']]);

respondSuccess([], 'Producto eliminado exitosamente');