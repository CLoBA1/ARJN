<?php
// api/dashboard/stats.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();

$stmtStats = $db->prepare("SELECT * FROM v_dashboard_stats");
$stmtStats->execute();
$kpis = $stmtStats->fetch();

$stmtAlertas = $db->prepare("SELECT * FROM v_alertas_stock LIMIT 10");
$stmtAlertas->execute();
$alertas = $stmtAlertas->fetchAll();

$stmtUltimosMov = $db->prepare("SELECT * FROM v_movimientos_completos ORDER BY created_at DESC LIMIT 5");
$stmtUltimosMov->execute();
$ultimosMov = $stmtUltimosMov->fetchAll();

// Productos por categoría
$stmtCat = $db->prepare("SELECT c.nombre as categoria, COUNT(p.id) as total FROM categorias c LEFT JOIN productos p ON c.id = p.categoria_id AND p.estado != 'inactivo' GROUP BY c.id");
$stmtCat->execute();
$cats = $stmtCat->fetchAll();
$colores = ['#198cbd', '#175a7f', '#C9A84C', '#2d8a4e', '#c0392b', '#d4820a', '#43484c'];
foreach($cats as $i => &$c) { $c['color'] = $colores[$i % count($colores)]; }

// Movimientos de los ultimos 7 dias
$movs = [];
for($i=6; $i>=0; $i--) {
    $fecha = date('Y-m-d', strtotime("-$i days"));
    $stmtE = $db->prepare("SELECT SUM(cantidad) FROM movimientos_inventario WHERE DATE(created_at) = ? AND tipo = 'entrada'");
    $stmtE->execute([$fecha]);
    $ent = $stmtE->fetchColumn() ?: 0;
    
    $stmtS = $db->prepare("SELECT SUM(cantidad) FROM movimientos_inventario WHERE DATE(created_at) = ? AND tipo = 'salida'");
    $stmtS->execute([$fecha]);
    $sal = $stmtS->fetchColumn() ?: 0;
    
    $movs[] = ["fecha" => $fecha, "entradas" => (int)$ent, "salidas" => (int)$sal];
}

respondSuccess([
    'data' => [
        'kpis' => $kpis,
        'movimientos_semana' => $movs,
        'productos_por_categoria' => $cats,
        'ultimos_movimientos' => $ultimosMov,
        'alertas_stock' => $alertas
    ]
]);