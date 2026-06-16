<?php
// api/productos/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();

$where = [];
$params = [];

if (!empty($_GET['categoria_id'])) {
    $where[] = "categoria_id = ?";
    $params[] = $_GET['categoria_id'];
}
if (!empty($_GET['estado'])) {
    $where[] = "estado = ?";
    $params[] = $_GET['estado'];
}
if (!empty($_GET['stock'])) {
    if ($_GET['stock'] === 'bajo') {
        $where[] = "stock_status = 'stock_bajo'";
    } elseif ($_GET['stock'] === 'sin_stock') {
        $where[] = "stock_status = 'sin_stock'";
    } elseif ($_GET['stock'] === 'ok') {
        $where[] = "stock_status = 'ok'";
    }
}
if (!empty($_GET['buscar'])) {
    $where[] = "(nombre LIKE ? OR sku LIKE ? OR descripcion LIKE ?)";
    $search = "%" . $_GET['buscar'] . "%";
    $params[] = $search;
    $params[] = $search;
    $params[] = $search;
}

$whereClause = $where ? "WHERE " . implode(" AND ", $where) : "";

// Contar totales
$stmtTotal = $db->prepare("SELECT COUNT(*) FROM v_productos_completos $whereClause");
$stmtTotal->execute($params);
$total = $stmtTotal->fetchColumn();

// Paginación
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
$offset = ($page - 1) * $limit;

// Orden
$allowedOrderBy = ['nombre', 'sku', 'precio_venta', 'stock_actual'];
$orderby = isset($_GET['orderby']) && in_array($_GET['orderby'], $allowedOrderBy) ? $_GET['orderby'] : 'nombre';
$order = isset($_GET['order']) && strtolower($_GET['order']) === 'desc' ? 'DESC' : 'ASC';

$sql = "SELECT * FROM v_productos_completos $whereClause ORDER BY $orderby $order LIMIT $limit OFFSET $offset";
$stmt = $db->prepare($sql);
$stmt->execute($params);
$productos = $stmt->fetchAll();

respond([
    'success' => true,
    'data' => $productos,
    'pagination' => [
        'total' => $total,
        'page' => $page,
        'limit' => $limit,
        'pages' => ceil($total / $limit)
    ]
]);