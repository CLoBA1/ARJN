<?php
// api/productos/update.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

$user = requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$data = json_decode(file_get_contents("php://input"));

if (empty($data->nombre) || strlen(trim($data->nombre)) < 3 || strlen(trim($data->nombre)) > 200) respondError('Nombre inválido');
if (empty($data->sku)) respondError('SKU requerido');
if (empty($data->categoria_id)) respondError('Categoría requerida');
if (!isset($data->precio_venta) || $data->precio_venta <= 0) respondError('Precio de venta inválido');
if (!isset($data->stock_actual) || $data->stock_actual < 0) respondError('Stock inválido');
if (!isset($data->stock_minimo) || $data->stock_minimo < 0) respondError('Stock mínimo inválido');

$db = (new Database())->getConnection();

// Verificar SKU excluyendo el propio producto
$stmtSku = $db->prepare("SELECT id FROM productos WHERE sku = ? AND id != ?");
$stmtSku->execute([trim($data->sku), $_GET['id']]);
if ($stmtSku->fetch()) respondError('SKU ya existe');

// Producto actual para ver stock anterior
$stmtProd = $db->prepare("SELECT stock_actual FROM productos WHERE id = ?");
$stmtProd->execute([$_GET['id']]);
$productoActual = $stmtProd->fetch();
if (!$productoActual) respondError('Producto no encontrado', 404);

try {
    $db->beginTransaction();

    $sql = "UPDATE productos SET nombre=?, sku=?, categoria_id=?, descripcion=?, precio_venta=?, precio_costo=?, stock_actual=?, stock_minimo=?, stock_maximo=?, unidad_medida=?, proveedor=?, imagen=?, estado=?, destacado=?, visible_tienda=?, notas=? WHERE id=?";
    
    $stmt = $db->prepare($sql);
    $stmt->execute([
        trim($data->nombre), trim($data->sku), $data->categoria_id, $data->descripcion ?? null,
        $data->precio_venta, $data->precio_costo ?? 0, $data->stock_actual, $data->stock_minimo,
        $data->stock_maximo ?? null, $data->unidad_medida ?? 'pieza', $data->proveedor ?? null,
        $data->imagen ?? null, $data->estado ?? 'activo', $data->destacado ?? 0,
        $data->visible_tienda ?? 1, $data->notas ?? null, $_GET['id']
    ]);

    // Registrar ajuste si cambió el stock manual
    if ($data->stock_actual != $productoActual['stock_actual']) {
        $cantidad = abs($data->stock_actual - $productoActual['stock_actual']);
        $tipo = $data->stock_actual > $productoActual['stock_actual'] ? 'entrada' : 'salida';
        
        $stmtMov = $db->prepare("INSERT INTO movimientos_inventario (producto_id, usuario_id, tipo, cantidad, stock_anterior, stock_nuevo, motivo) VALUES (?, ?, ?, ?, ?, ?, 'ajuste_manual')");
        $stmtMov->execute([$_GET['id'], $user['id'], $tipo, $cantidad, $productoActual['stock_actual'], $data->stock_actual]);
    }

    $db->commit();
    respondSuccess([], 'Producto actualizado exitosamente');

} catch (Exception $e) {
    $db->rollBack();
    respondError('Error al actualizar producto: ' . $e->getMessage(), 500);
}