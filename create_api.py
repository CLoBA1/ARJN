import os
import sys

base_dir = r"c:\xampp\htdocs\ARN 2026\api"

files = {
    "config/database.php": """<?php
// api/config/database.php
class Database {
  private $host     = '127.0.0.1';
  private $db_name  = 'u707366501_JN_db';
  private $username = 'u707366501_FF';
  private $password = '11O324LizE@';
  private $charset  = 'utf8mb4';
  private $conn     = null;

  public function getConnection() {
    if ($this->conn !== null) return $this->conn;
    try {
      $dsn = "mysql:host={$this->host};dbname={$this->db_name};charset={$this->charset}";
      $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
      ];
      $this->conn = new PDO($dsn, $this->username, $this->password, $options);
    } catch (PDOException $e) {
      http_response_code(500);
      echo json_encode([
        'success' => false,
        'message' => 'Error de conexión a la base de datos'
      ]);
      exit;
    }
    return $this->conn;
  }
}
""",
    "config/cors.php": """<?php
// api/config/cors.php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Session-Token');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
  http_response_code(200);
  exit;
}

function respond($data, $code = 200) {
  http_response_code($code);
  echo json_encode($data, JSON_UNESCAPED_UNICODE);
  exit;
}

function respondError($message, $code = 400) {
  respond(['success' => false, 'message' => $message], $code);
}

function respondSuccess($data = [], $message = 'OK') {
  respond(array_merge(['success' => true, 'message' => $message], $data));
}
""",
    "config/auth.php": """<?php
// api/config/auth.php
require_once __DIR__ . '/database.php';

function generateToken() {
    return bin2hex(random_bytes(32));
}

function saveSession($userId, $token) {
    $db = (new Database())->getConnection();
    $stmt = $db->prepare("INSERT INTO sesiones (id, usuario_id, ip, user_agent, expires_at) VALUES (?, ?, ?, ?, DATE_ADD(NOW(), INTERVAL 8 HOUR))");
    $stmt->execute([$token, $userId, $_SERVER['REMOTE_ADDR'] ?? null, $_SERVER['HTTP_USER_AGENT'] ?? null]);
}

function validateToken($token) {
    if (!$token) return false;
    $db = (new Database())->getConnection();
    $stmt = $db->prepare("SELECT u.* FROM sesiones s JOIN usuarios u ON s.usuario_id = u.id WHERE s.id = ? AND s.expires_at > NOW() AND u.estado = 'activo'");
    $stmt->execute([$token]);
    return $stmt->fetch();
}

function requireAuth() {
    $headers = getallheaders();
    $token = $headers['X-Session-Token'] ?? $_SERVER['HTTP_X_SESSION_TOKEN'] ?? null;
    $user = validateToken($token);
    if (!$user) {
        respondError('No autorizado o sesión expirada', 401);
    }
    return $user;
}

function requireAdmin() {
    $user = requireAuth();
    if ($user['rol'] !== 'admin') {
        respondError('Acceso denegado, se requiere rol de administrador', 403);
    }
    return $user;
}
""",
    "auth/login.php": """<?php
// api/auth/login.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));
if (empty($data->username) || empty($data->password)) {
    respondError('Usuario y contraseña son requeridos');
}

$db = (new Database())->getConnection();
$stmt = $db->prepare("SELECT * FROM usuarios WHERE username = ? AND estado = 'activo'");
$stmt->execute([trim($data->username)]);
$user = $stmt->fetch();

if ($user && password_verify($data->password, $user['password'])) {
    $token = generateToken();
    saveSession($user['id'], $token);
    
    $stmtUpdate = $db->prepare("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = ?");
    $stmtUpdate->execute([$user['id']]);
    
    unset($user['password']);
    respondSuccess([
        'token' => $token,
        'usuario' => $user,
        'expires_at' => date('Y-m-d H:i:s', strtotime('+8 hours'))
    ], 'Login exitoso');
} else {
    respondError('Credenciales incorrectas', 401);
}
""",
    "auth/logout.php": """<?php
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
""",
    "productos/index.php": """<?php
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
""",
    "productos/show.php": """<?php
// api/productos/show.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$db = (new Database())->getConnection();

$stmt = $db->prepare("SELECT * FROM v_productos_completos WHERE id = ?");
$stmt->execute([$_GET['id']]);
$producto = $stmt->fetch();

if (!$producto) respondError('Producto no encontrado', 404);

$stmtMov = $db->prepare("SELECT * FROM v_movimientos_completos WHERE producto_id = ? ORDER BY created_at DESC LIMIT 5");
$stmtMov->execute([$_GET['id']]);
$movimientos = $stmtMov->fetchAll();

$producto['movimientos'] = $movimientos;

respondSuccess($producto);
""",
    "productos/store.php": """<?php
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
""",
    "productos/update.php": """<?php
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
""",
    "productos/delete.php": """<?php
// api/productos/delete.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'DELETE') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$db = (new Database())->getConnection();

// Soft delete
$stmt = $db->prepare("UPDATE productos SET estado = 'inactivo' WHERE id = ?");
$stmt->execute([$_GET['id']]);

respondSuccess([], 'Producto eliminado exitosamente');
""",
    "categorias/index.php": """<?php
// api/categorias/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAuth();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();

$sql = "SELECT c.*, (SELECT COUNT(*) FROM productos p WHERE p.categoria_id = c.id AND p.estado != 'inactivo') as total_productos FROM categorias c WHERE c.estado = 'activo' ORDER BY c.orden ASC";
$stmt = $db->prepare($sql);
$stmt->execute();
$categorias = $stmt->fetchAll();

respondSuccess(['data' => $categorias]);
""",
    "categorias/store.php": """<?php
// api/categorias/store.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));
if (empty($data->nombre)) respondError('El nombre es requerido');

$slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $data->nombre)));

$db = (new Database())->getConnection();
$stmt = $db->prepare("INSERT INTO categorias (nombre, descripcion, icono, slug, orden) VALUES (?, ?, ?, ?, ?)");
$stmt->execute([
    trim($data->nombre), 
    $data->descripcion ?? null, 
    $data->icono ?? null, 
    $slug, 
    $data->orden ?? 0
]);

respondSuccess(['id' => $db->lastInsertId()], 'Categoría creada exitosamente');
""",
    "categorias/update.php": """<?php
// api/categorias/update.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$data = json_decode(file_get_contents("php://input"));
if (empty($data->nombre)) respondError('El nombre es requerido');

$slug = strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $data->nombre)));

$db = (new Database())->getConnection();
$stmt = $db->prepare("UPDATE categorias SET nombre = ?, descripcion = ?, icono = ?, slug = ?, orden = ? WHERE id = ?");
$stmt->execute([
    trim($data->nombre), 
    $data->descripcion ?? null, 
    $data->icono ?? null, 
    $slug, 
    $data->orden ?? 0,
    $_GET['id']
]);

respondSuccess([], 'Categoría actualizada exitosamente');
""",
    "movimientos/index.php": """<?php
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
""",
    "movimientos/store.php": """<?php
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
""",
    "usuarios/index.php": """<?php
// api/usuarios/index.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'GET') respondError('Método no permitido', 405);

$db = (new Database())->getConnection();
$stmt = $db->prepare("SELECT id, nombre, username, rol, estado, avatar, ultimo_acceso, created_at, updated_at FROM usuarios WHERE estado != 'eliminado'");
$stmt->execute();
$usuarios = $stmt->fetchAll();

respondSuccess(['data' => $usuarios]);
""",
    "usuarios/store.php": """<?php
// api/usuarios/store.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') respondError('Método no permitido', 405);

$data = json_decode(file_get_contents("php://input"));

if (empty($data->nombre)) respondError('El nombre es requerido');
if (empty($data->username)) respondError('El username es requerido');
if (empty($data->password)) respondError('La contraseña es requerida');

$db = (new Database())->getConnection();

// Verificar username único
$stmtUser = $db->prepare("SELECT id FROM usuarios WHERE username = ?");
$stmtUser->execute([trim($data->username)]);
if ($stmtUser->fetch()) respondError('El nombre de usuario ya está en uso');

$hash = password_hash($data->password, PASSWORD_BCRYPT);

$stmt = $db->prepare("INSERT INTO usuarios (nombre, username, password, rol, estado, avatar) VALUES (?, ?, ?, ?, ?, ?)");
$stmt->execute([
    trim($data->nombre), trim($data->username), $hash, 
    $data->rol ?? 'empleado', $data->estado ?? 'activo', 
    $data->avatar ?? null
]);

respondSuccess(['id' => $db->lastInsertId()], 'Usuario creado exitosamente');
""",
    "usuarios/update.php": """<?php
// api/usuarios/update.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

$data = json_decode(file_get_contents("php://input"));

if (empty($data->nombre)) respondError('El nombre es requerido');
if (empty($data->username)) respondError('El username es requerido');

$db = (new Database())->getConnection();

$stmtUser = $db->prepare("SELECT id FROM usuarios WHERE username = ? AND id != ?");
$stmtUser->execute([trim($data->username), $_GET['id']]);
if ($stmtUser->fetch()) respondError('El nombre de usuario ya está en uso');

if (!empty($data->password)) {
    $hash = password_hash($data->password, PASSWORD_BCRYPT);
    $stmt = $db->prepare("UPDATE usuarios SET nombre=?, username=?, password=?, rol=?, estado=?, avatar=? WHERE id=?");
    $stmt->execute([trim($data->nombre), trim($data->username), $hash, $data->rol ?? 'empleado', $data->estado ?? 'activo', $data->avatar ?? null, $_GET['id']]);
} else {
    $stmt = $db->prepare("UPDATE usuarios SET nombre=?, username=?, rol=?, estado=?, avatar=? WHERE id=?");
    $stmt->execute([trim($data->nombre), trim($data->username), $data->rol ?? 'empleado', $data->estado ?? 'activo', $data->avatar ?? null, $_GET['id']]);
}

respondSuccess([], 'Usuario actualizado exitosamente');
""",
    "usuarios/delete.php": """<?php
// api/usuarios/delete.php
require_once '../config/cors.php';
require_once '../config/database.php';
require_once '../config/auth.php';

$user = requireAdmin();

if ($_SERVER['REQUEST_METHOD'] !== 'DELETE') respondError('Método no permitido', 405);
if (empty($_GET['id'])) respondError('ID requerido');

if ($user['id'] == $_GET['id']) respondError('No puedes desactivar tu propia cuenta', 400);

$db = (new Database())->getConnection();
$stmt = $db->prepare("UPDATE usuarios SET estado = 'inactivo' WHERE id = ?");
$stmt->execute([$_GET['id']]);

respondSuccess([], 'Usuario desactivado exitosamente');
""",
    "dashboard/stats.php": """<?php
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
""",
    "reportes/index.php": """<?php
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
""",
    "configuracion/index.php": """<?php
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
""",
    "configuracion/update.php": """<?php
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
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n")

print(f"Created {len(files)} PHP files successfully.")
