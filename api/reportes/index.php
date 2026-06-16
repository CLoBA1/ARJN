<?php
// api/reportes/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$tipo = $_GET['tipo'] ?? null;
$desde = $_GET['desde'] ?? null;
$hasta = $_GET['hasta'] ?? null;

$db = (new Database())->getConnection();
$data = [];

if ($tipo === 'inventario') {
    $stmt = $db->prepare("SELECT p.nombre, p.sku, c.nombre as categoria, p.stock_actual, p.precio_venta, (p.stock_actual * p.precio_venta) as valor_total FROM productos p JOIN categorias c ON p.categoria_id = c.id WHERE p.estado != 'inactivo'");
    $stmt->execute();
    $data = $stmt->fetchAll();
} elseif ($tipo === 'movimientos') {
    $where = [];
    $params = [];
    if($desde) { $where[] = "created_at >= ?"; $params[] = $desde . ' 00:00:00'; }
    if($hasta) { $where[] = "created_at <= ?"; $params[] = $hasta . ' 23:59:59'; }
    $wc = $where ? "WHERE " . implode(" AND ", $where) : "";
    $stmt = $db->prepare("SELECT * FROM v_movimientos_completos $wc ORDER BY created_at DESC");
    $stmt->execute($params);
    $data = $stmt->fetchAll();
} elseif ($tipo === 'top_productos') {
    $stmt = $db->prepare("SELECT p.nombre, p.sku, SUM(m.cantidad) as total_movido FROM movimientos_inventario m JOIN productos p ON m.producto_id = p.id GROUP BY p.id ORDER BY total_movido DESC LIMIT 10");
    $stmt->execute();
    $data = $stmt->fetchAll();
} elseif ($tipo === 'valorizacion') {
    $stmt = $db->prepare("SELECT c.nombre as categoria, COUNT(p.id) as productos, SUM(p.stock_actual * p.precio_costo) as costo_total, SUM(p.stock_actual * p.precio_venta) as valor_venta FROM categorias c LEFT JOIN productos p ON c.id = p.categoria_id AND p.estado != 'inactivo' GROUP BY c.id");
    $stmt->execute();
    $data = $stmt->fetchAll();
}

respondSuccess(['data' => $data]);