<?php
// api/configuracion/update.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));
$db = (new Database())->getConnection();

if (isset($data->config) && is_object($data->config)) {
    $stmt = $db->prepare("UPDATE configuracion SET valor = ? WHERE clave = ?");
    foreach($data->config as $k => $v) {
        $stmt->execute([$v, $k]);
    }
} elseif (isset($data->clave) && isset($data->valor)) {
    $stmt = $db->prepare("UPDATE configuracion SET valor = ? WHERE clave = ?");
    $stmt->execute([$data->valor, $data->clave]);
}

respondSuccess([], 'Configuración actualizada');