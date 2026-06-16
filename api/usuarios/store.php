<?php
// api/usuarios/store.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));

if (empty($data->nombre)) respondError('El nombre es requerido');
if (empty($data->username)) respondError('El username es requerido');
if (empty($data->password)) respondError('La contraseña es requerida');

$db = (new Database())->getConnection();

// Verificar username único
$stmtUser = $db->prepare("SELECT id FROM usuarios WHERE username = ?");
$stmtUser->execute([trim($data->username)]);
if ($stmtUser->fetch()) respondError('El nombre de usuario ya está en uso');

$hash = password_hash($data->password, PASSWORD_BCRYPT);

$stmt = $db->prepare("INSERT INTO usuarios (nombre, username, password, rol, estado, avatar) VALUES (?, ?, ?, ?, ?, ?)");
$stmt->execute([
    trim($data->nombre), trim($data->username), $hash, 
    $data->rol ?? 'empleado', $data->estado ?? 'activo', 
    $data->avatar ?? null
]);

respondSuccess(['id' => $db->lastInsertId()], 'Usuario creado exitosamente');