<?php
// api/auth/logout.php
require_once '../config/cors.php';
require_once '../config/database.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$headers = getallheaders();
$token = $headers['X-Session-Token'] ?? $_SERVER['HTTP_X_SESSION_TOKEN'] ?? null;

if ($token) {
    $db = (new Database())->getConnection();
    $stmt = $db->prepare("DELETE FROM sesiones WHERE id = ?");
    $stmt->execute([$token]);
}

respondSuccess([], 'Sesión cerrada');