<?php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';
requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'DELETE') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));
if (empty($data->id)) respondError('ID requerido');

$db = (new Database())->getConnection();

// Verificar que no tenga productos activos
$check = $db->prepare("SELECT COUNT(*) as total FROM productos WHERE categoria_id = ? AND estado != 'inactivo'");
$check->execute([$data->id]);
$count = $check->fetch();
if ($count['total'] > 0) {
    respondError('No se puede eliminar: la categoría tiene ' . $count['total'] . ' producto(s) activo(s)', 409);
}

$stmt = $db->prepare("UPDATE categorias SET estado = 'inactivo' WHERE id = ?");
$stmt->execute([$data->id]);

if ($stmt->rowCount() === 0) respondError('Categoría no encontrada', 404);

respondSuccess(null, 'Categoría eliminada correctamente');
