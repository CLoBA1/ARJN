<?php
// api/productos/store.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

$user = requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));

if (empty($data->nombre) || strlen(trim($data->nombre)) < 3 || strlen(trim($data->nombre)) > 200) respondError('Nombre inválido');
if (empty($data->sku)) respondError('SKU requerido');
if (empty($data->categoria_id)) respondError('Categoría requerida');
if (!isset($data->precio_venta) || $data->precio_venta <= 0) respondError('Precio de venta inválido');
if (!isset($data->stock_actual) || $data->stock_actual < 0) respondError('Stock inválido');
if (!isset($data->stock_minimo) || $data->stock_minimo < 0) respondError('Stock mínimo inválido');

$db = (new Database())->getConnection();

// Verificar SKU
$stmtSku = $db->prepare("SELECT id FROM productos WHERE sku = ?");
$stmtSku->execute([trim($data->sku)]);
if ($stmtSku->fetch()) respondError('SKU ya existe');

// Verificar Categoría
$stmtCat = $db->prepare("SELECT id FROM categorias WHERE id = ?");
$stmtCat->execute([$data->categoria_id]);
if (!$stmtCat->fetch()) respondError('Categoría no existe');

try {
    $db->beginTransaction();

    $sql = "INSERT INTO productos (nombre, sku, categoria_id, descripcion, precio_venta, precio_costo, stock_actual, stock_minimo, stock_maximo, unidad_medida, proveedor, imagen, estado, destacado, visible_tienda, notas, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    
    $stmt = $db->prepare($sql);
    $stmt->execute([
        trim($data->nombre), trim($data->sku), $data->categoria_id, $data->descripcion ?? null,
        $data->precio_venta, $data->precio_costo ?? 0, $data->stock_actual, $data->stock_minimo,
        $data->stock_maximo ?? null, $data->unidad_medida ?? 'pieza', $data->proveedor ?? null,
        $data->imagen ?? null, $data->estado ?? 'activo', $data->destacado ?? 0,
        $data->visible_tienda ?? 1, $data->notas ?? null, $user['id']
    ]);

    $productoId = $db->lastInsertId();

    if ($data->stock_actual > 0) {
        $stmtMov = $db->prepare("INSERT INTO movimientos_inventario (producto_id, usuario_id, tipo, cantidad, stock_anterior, stock_nuevo, motivo) VALUES (?, ?, 'entrada', ?, 0, ?, 'compra')");
        $stmtMov->execute([$productoId, $user['id'], $data->stock_actual, $data->stock_actual]);
    }

    $db->commit();
    respondSuccess(['id' => $productoId], 'Producto creado exitosamente');

} catch (Exception $e) {
    $db->rollBack();
    respondError('Error al crear producto: ' . $e->getMessage(), 500);
}