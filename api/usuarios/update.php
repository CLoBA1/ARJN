<?php
// api/usuarios/update.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$data = json_decode(file_get_contents("php://input"));

if (empty($data->nombre)) respondError('El nombre es requerido');
if (empty($data->username)) respondError('El username es requerido');

$db = (new Database())->getConnection();

$stmtUser = $db->prepare("SELECT id FROM usuarios WHERE username = ? AND id != ?");
$stmtUser->execute([trim($data->username), $_GET['id']]);
if ($stmtUser->fetch()) respondError('El nombre de usuario ya está en uso');

if (!empty($data->password)) {
    $hash = password_hash($data->password, PASSWORD_BCRYPT);
    $stmt = $db->prepare("UPDATE usuarios SET nombre=?, username=?, password=?, rol=?, estado=?, avatar=? WHERE id=?");
    $stmt->execute([trim($data->nombre), trim($data->username), $hash, $data->rol ?? 'empleado', $data->estado ?? 'activo', $data->avatar ?? null, $_GET['id']]);
} else {
    $stmt = $db->prepare("UPDATE usuarios SET nombre=?, username=?, rol=?, estado=?, avatar=? WHERE id=?");
    $stmt->execute([trim($data->nombre), trim($data->username), $data->rol ?? 'empleado', $data->estado ?? 'activo', $data->avatar ?? null, $_GET['id']]);
}

respondSuccess([], 'Usuario actualizado exitosamente');