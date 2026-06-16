<?php
// api/auth/login.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));
if (empty($data->username) || empty($data->password)) {
    respondError('Usuario y contraseña son requeridos');
}

$db = (new Database())->getConnection();
$stmt = $db->prepare("SELECT * FROM usuarios WHERE username = ? AND estado = 'activo'");
$stmt->execute([trim($data->username)]);
$user = $stmt->fetch();

if ($user && password_verify($data->password, $user['password'])) {
    $token = generateToken();
    saveSession($user['id'], $token);
    
    $stmtUpdate = $db->prepare("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = ?");
    $stmtUpdate->execute([$user['id']]);
    
    unset($user['password']);
    respondSuccess([
        'token' => $token,
        'usuario' => $user,
        'expires_at' => date('Y-m-d H:i:s', strtotime('+8 hours'))
    ], 'Login exitoso');
} else {
    respondError('Credenciales incorrectas', 401);
}