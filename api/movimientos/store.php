<?php
// api/movimientos/store.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

$user = requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));

if (empty($data->producto_id)) respondError('Producto requerido');
if (empty($data->tipo) || !in_array($data->tipo, ['entrada', 'salida', 'ajuste'])) respondError('Tipo de movimiento inválido');
if (!isset($data->cantidad) || $data->cantidad <= 0) respondError('La cantidad debe ser mayor a 0');
if (empty($data->motivo)) respondError('Motivo requerido');

$db = (new Database())->getConnection();

try {
    $db->beginTransaction();

    $stmtProd = $db->prepare("SELECT stock_actual, estado FROM productos WHERE id = ? AND estado != 'inactivo' FOR UPDATE");
    $stmtProd->execute([$data->producto_id]);
    $producto = $stmtProd->fetch();

    if (!$producto) {
        throw new Exception('Producto no encontrado o inactivo');
    }

    $stock_anterior = $producto['stock_actual'];
    $stock_nuevo = 0;

    if ($data->tipo === 'entrada') {
        $stock_nuevo = $stock_anterior + $data->cantidad;
    } elseif ($data->tipo === 'salida') {
        if ($stock_anterior < $data->cantidad) {
            throw new Exception('Stock insuficiente para la salida');
        }
        $stock_nuevo = $stock_anterior - $data->cantidad;
    } elseif ($data->tipo === 'ajuste') {
        $stock_nuevo = $data->cantidad; // Aqui asumimos que envian el nuevo stock exacto si es ajuste, o la diferencia? El prompt dice "stock_nuevo = cantidad (valor absoluto)"
    }

    // Actualizar producto
    $nuevo_estado = $stock_nuevo == 0 ? 'agotado' : 'activo';
    $stmtUpdProd = $db->prepare("UPDATE productos SET stock_actual = ?, estado = ? WHERE id = ?");
    $stmtUpdProd->execute([$stock_nuevo, $nuevo_estado, $data->producto_id]);

    // Registrar movimiento
    $stmtMov = $db->prepare("INSERT INTO movimientos_inventario (producto_id, usuario_id, tipo, cantidad, stock_anterior, stock_nuevo, motivo, referencia, notas) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");
    $stmtMov->execute([
        $data->producto_id, $user['id'], $data->tipo, $data->cantidad, 
        $stock_anterior, $stock_nuevo, $data->motivo, 
        $data->referencia ?? null, $data->notas ?? null
    ]);

    $db->commit();
    respondSuccess(['stock_nuevo' => $stock_nuevo], 'Movimiento registrado exitosamente');

} catch (Exception $e) {
    $db->rollBack();
    respondError('Error: ' . $e->getMessage(), 400);
}