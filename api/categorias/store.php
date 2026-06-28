<?php
// api/categorias/store.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));
if (empty($data->nombre)) respondError('El nombre es requerido');
$prefijo = !empty($data->prefijo) ? strtoupper(trim($data->prefijo)) : null;

$slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $data->nombre)));

$db = (new Database())->getConnection();
$stmt = $db->prepare("INSERT INTO categorias (nombre, prefijo, descripcion, icono, slug, orden) VALUES (?, ?, ?, ?, ?, ?)");
$stmt->execute([
    trim($data->nombre),
    $prefijo,
    $data->descripcion ?? null,
    $data->icono ?? null,
    $slug,
    $data->orden ?? 0
]);

respondSuccess(['id' => $db->lastInsertId()], 'Categoría creada exitosamente');