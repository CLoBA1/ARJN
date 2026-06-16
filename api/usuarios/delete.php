<?php
// api/usuarios/delete.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

$user = requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'DELETE') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

if ($user['id'] == $_GET['id']) respondError('No puedes desactivar tu propia cuenta', 400);

$db = (new Database())->getConnection();
$stmt = $db->prepare("UPDATE usuarios SET estado = 'inactivo' WHERE id = ?");
$stmt->execute([$_GET['id']]);

respondSuccess([], 'Usuario desactivado exitosamente');