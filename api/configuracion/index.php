<?php
// api/configuracion/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();
$stmt = $db->prepare("SELECT clave, valor, tipo FROM configuracion");
$stmt->execute();
$config = [];
while($row = $stmt->fetch()) {
    $config[$row['clave']] = $row['tipo'] === 'numero' ? (float)$row['valor'] : ($row['tipo'] === 'booleano' ? (bool)$row['valor'] : $row['valor']);
}

respondSuccess(['data' => $config]);