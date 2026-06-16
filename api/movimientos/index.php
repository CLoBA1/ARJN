<?php
// api/movimientos/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();

$where = [];
$params = [];

if (!empty($_GET['producto_id'])) {
    $where[] = "producto_id = ?";
    $params[] = $_GET['producto_id'];
}
if (!empty($_GET['tipo'])) {
    $where[] = "tipo = ?";
    $params[] = $_GET['tipo'];
}
if (!empty($_GET['desde'])) {
    $where[] = "created_at >= ?";
    $params[] = $_GET['desde'] . ' 00:00:00';
}
if (!empty($_GET['hasta'])) {
    $where[] = "created_at <= ?";
    $params[] = $_GET['hasta'] . ' 23:59:59';
}
if (!empty($_GET['usuario_id'])) {
    $where[] = "usuario_id = ?";
    $params[] = $_GET['usuario_id'];
}

$whereClause = $where ? "WHERE " . implode(" AND ", $where) : "";

$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 50;
$offset = ($page - 1) * $limit;

$stmtTotal = $db->prepare("SELECT COUNT(*) FROM v_movimientos_completos $whereClause");
$stmtTotal->execute($params);
$total = $stmtTotal->fetchColumn();

$sql = "SELECT * FROM v_movimientos_completos $whereClause ORDER BY created_at DESC LIMIT $limit OFFSET $offset";
$stmt = $db->prepare($sql);
$stmt->execute($params);
$movimientos = $stmt->fetchAll();

respond([
    'success' => true,
    'data' => $movimientos,
    'pagination' => [
        'total' => $total,
        'page' => $page,
        'limit' => $limit,
        'pages' => ceil($total / $limit)
    ]
]);