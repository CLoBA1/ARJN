<?php
// api/categorias/update.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$data = json_decode(file_get_contents("php://input"));
if (empty($data->nombre)) respondError('El nombre es requerido');

$slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $data->nombre)));

$db = (new Database())->getConnection();
$stmt = $db->prepare("UPDATE categorias SET nombre = ?, descripcion = ?, icono = ?, slug = ?, orden = ? WHERE id = ?");
$stmt->execute([
    trim($data->nombre), 
    $data->descripcion ?? null, 
    $data->icono ?? null, 
    $slug, 
    $data->orden ?? 0,
    $_GET['id']
]);

respondSuccess([], 'Categoría actualizada exitosamente');