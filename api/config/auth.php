<?php
// api/config/auth.php
require_once __DIR__ . '/database.php';

function generateToken() {
    return bin2hex(random_bytes(32));
}

function saveSession($userId, $token) {
    $db = (new Database())->getConnection();
    $stmt = $db->prepare("INSERT INTO sesiones (id, usuario_id, ip, user_agent, expires_at) VALUES (?, ?, ?, ?, DATE_ADD(NOW(), INTERVAL 8 HOUR))");
    $stmt->execute([$token, $userId, $_SERVER['REMOTE_ADDR'] ?? null, $_SERVER['HTTP_USER_AGENT'] ?? null]);
}

function validateToken($token) {
    if (!$token) return false;
    $db = (new Database())->getConnection();
    $stmt = $db->prepare("SELECT u.* FROM sesiones s JOIN usuarios u ON s.usuario_id = u.id WHERE s.id = ? AND s.expires_at > NOW() AND u.estado = 'activo'");
    $stmt->execute([$token]);
    return $stmt->fetch();
}

function requireAuth() {
    $headers = getallheaders();
    $token = $headers['X-Session-Token'] ?? $_SERVER['HTTP_X_SESSION_TOKEN'] ?? null;
    $user = validateToken($token);
    if (!$user) {
        respondError('No autorizado o sesión expirada', 401);
    }
    return $user;
}

function requireAdmin() {
    $user = requireAuth();
    if ($user['rol'] !== 'admin') {
        respondError('Acceso denegado, se requiere rol de administrador', 403);
    }
    return $user;
}