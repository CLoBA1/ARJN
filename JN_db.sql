-- phpMyAdmin SQL Dump
-- Generado para el proyecto e-commerce "Jesús de Nazaret"
-- Base de datos: `JN_db`

-- ═══════════════════════════════════════
-- ⚙️ CONFIGURACIÓN INICIAL
-- ═══════════════════════════════════════
-- Crear y seleccionar la base de datos
CREATE DATABASE IF NOT EXISTS JN_db 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE JN_db;

-- Desactivar verificación de claves foráneas durante la creación
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


-- ═══════════════════════════════════════
-- 📋 TABLA 1: usuarios
-- ═══════════════════════════════════════
CREATE TABLE usuarios (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(100) NOT NULL,
  username    VARCHAR(50)  NOT NULL UNIQUE,
  password    VARCHAR(255) NOT NULL,  -- bcrypt hash
  rol         ENUM('admin','empleado') NOT NULL DEFAULT 'empleado',
  estado      ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  avatar      TEXT NULL,              -- base64 o URL
  ultimo_acceso DATETIME NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos iniciales usuarios
-- Passwords hasheadas con bcrypt. 
-- El hash proporcionado '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi' corresponde a 'admin123'
-- Se usa como referencia para los 3 usuarios de prueba solicitados.
INSERT INTO usuarios (nombre, username, password, rol, estado) VALUES
('Carlos Mendoza', 'admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin', 'activo'),
('María López', 'empleado', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'empleado', 'activo'),
('Roberto Sánchez', 'roberto', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'empleado', 'inactivo');


-- ═══════════════════════════════════════
-- 📋 TABLA 2: categorias
-- ═══════════════════════════════════════
CREATE TABLE categorias (
  id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(100) NOT NULL,
  descripcion TEXT NULL,
  icono       VARCHAR(50)  NULL,      -- nombre del ícono SVG
  slug        VARCHAR(100) NOT NULL UNIQUE,
  estado      ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
  orden       INT UNSIGNED DEFAULT 0, -- para ordenar en el frontend
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos iniciales categorias
INSERT INTO categorias (id, nombre, slug, orden) VALUES
(1, 'Imágenes y Santos', 'imagenes-santos', 1),
(2, 'Velas y Veladoras', 'velas-veladoras', 2),
(3, 'Rosarios y Medallas', 'rosarios-medallas', 3),
(4, 'Libros y Biblias', 'libros-biblias', 4),
(5, 'Incienso y Sahumerios', 'incienso-sahumerios', 5),
(6, 'Artículos Litúrgicos', 'articulos-liturgicos', 6),
(7, 'Joyería Religiosa', 'joyeria-religiosa', 7);


-- ═══════════════════════════════════════
-- 📋 TABLA 3: productos
-- ═══════════════════════════════════════
CREATE TABLE productos (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(200) NOT NULL,
  sku             VARCHAR(50)  NOT NULL UNIQUE,
  categoria_id    INT UNSIGNED NOT NULL,
  descripcion     TEXT NULL,
  precio_venta    DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  precio_costo    DECIMAL(10,2) NULL DEFAULT 0.00,
  stock_actual    INT NOT NULL DEFAULT 0,
  stock_minimo    INT NOT NULL DEFAULT 5,
  stock_maximo    INT NULL DEFAULT 100,
  unidad_medida   ENUM('pieza','caja','kg','litro','paquete','rollo') NOT NULL DEFAULT 'pieza',
  proveedor       VARCHAR(150) NULL,
  imagen          LONGTEXT NULL,      -- base64 de la imagen
  imagen_url      VARCHAR(500) NULL,  -- URL alternativa
  estado          ENUM('activo','inactivo','agotado') NOT NULL DEFAULT 'activo',
  destacado       TINYINT(1) DEFAULT 0, -- para mostrar en home del ecommerce
  visible_tienda  TINYINT(1) DEFAULT 1, -- visible en ecommerce público
  notas           TEXT NULL,
  created_by      INT UNSIGNED NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT,
  FOREIGN KEY (created_by)   REFERENCES usuarios(id)   ON DELETE SET NULL,
  
  INDEX idx_sku (sku),
  INDEX idx_categoria (categoria_id),
  INDEX idx_estado (estado),
  INDEX idx_stock (stock_actual),
  INDEX idx_destacado (destacado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos iniciales productos (15 productos de ejemplo)
INSERT INTO productos (nombre, sku, categoria_id, precio_venta, precio_costo, stock_actual, stock_minimo, estado, created_by) VALUES
-- Imágenes y Santos
('Imagen San José 30cm', 'JN-IMG-001', 1, 450.00, 280.00, 12, 3, 'activo', 1),
('Imagen Virgen de Guadalupe 45cm', 'JN-IMG-002', 1, 680.00, 420.00, 0, 2, 'agotado', 1),
('Cristo Crucifijo Madera 60cm', 'JN-IMG-003', 1, 890.00, 550.00, 5, 2, 'activo', 1),
-- Velas y Veladoras
('Vela Pascual 60cm', 'JN-VEL-001', 2, 320.00, 180.00, 8, 10, 'activo', 1),
('Veladora 7 Días Azul', 'JN-VEL-002', 2, 45.00, 22.00, 65, 20, 'activo', 1),
('Cirio Bautismal 40cm', 'JN-VEL-003', 2, 180.00, 95.00, 3, 5, 'activo', 1),
-- Rosarios y Medallas
('Rosario Madera de Olivo', 'JN-ROS-001', 3, 285.00, 150.00, 45, 10, 'activo', 1),
('Rosario Nácar Blanco', 'JN-ROS-002', 3, 420.00, 220.00, 18, 8, 'activo', 1),
('Medalla San Cristóbal Plata', 'JN-MED-001', 3, 320.00, 180.00, 0, 5, 'agotado', 1),
-- Libros y Biblias
('Biblia de Jerusalén', 'JN-LIB-001', 4, 680.00, 380.00, 22, 5, 'activo', 1),
('Misal Romano Completo', 'JN-LIB-002', 4, 450.00, 250.00, 9, 4, 'activo', 1),
-- Incienso y Sahumerios
('Incienso Mirra 500g', 'JN-INC-001', 5, 180.00, 90.00, 3, 10, 'activo', 1),
('Sahumerio Copal Natural', 'JN-INC-002', 5, 95.00, 45.00, 28, 8, 'activo', 1),
-- Artículos Litúrgicos
('Cáliz Dorado Clásico', 'JN-LIT-001', 6, 2800.00, 1800.00, 4, 2, 'activo', 1),
('Patena Plateada', 'JN-LIT-002', 6, 950.00, 580.00, 6, 2, 'activo', 1),
-- Joyería Religiosa
('Cruz Pectoral Oro Laminado', 'JN-JOY-001', 7, 780.00, 420.00, 11, 3, 'activo', 1);


-- ═══════════════════════════════════════
-- 📋 TABLA 4: movimientos_inventario
-- ═══════════════════════════════════════
CREATE TABLE movimientos_inventario (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  producto_id     INT UNSIGNED NOT NULL,
  usuario_id      INT UNSIGNED NULL,
  tipo            ENUM('entrada','salida','ajuste') NOT NULL,
  cantidad        INT NOT NULL,              -- siempre positivo
  stock_anterior  INT NOT NULL,
  stock_nuevo     INT NOT NULL,
  motivo          ENUM('compra','venta','devolucion','dano','inventario','ajuste_manual','otro') NOT NULL DEFAULT 'otro',
  referencia      VARCHAR(100) NULL,         -- número de orden/factura
  notas           TEXT NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  FOREIGN KEY (usuario_id)  REFERENCES usuarios(id)  ON DELETE SET NULL,
  
  INDEX idx_producto   (producto_id),
  INDEX idx_usuario    (usuario_id),
  INDEX idx_tipo       (tipo),
  INDEX idx_fecha      (created_at),
  INDEX idx_motivo     (motivo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos iniciales movimientos (10 movimientos de ejemplo)
INSERT INTO movimientos_inventario (producto_id, usuario_id, tipo, cantidad, stock_anterior, stock_nuevo, motivo, created_at) VALUES
(7, 1, 'entrada', 50, 0, 50, 'compra', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 30 DAY)),
(7, 2, 'salida', 5, 50, 45, 'venta', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 28 DAY)),
(4, 1, 'entrada', 20, 0, 20, 'compra', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 20 DAY)),
(4, 2, 'salida', 12, 20, 8, 'venta', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 15 DAY)),
(12, 1, 'ajuste', 0, 3, 3, 'inventario', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 10 DAY)),
(10, 1, 'entrada', 15, 7, 22, 'compra', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 8 DAY)),
(14, 1, 'salida', 3, 7, 4, 'venta', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 5 DAY)),
(1, 2, 'salida', 2, 14, 12, 'venta', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)),
(5, 2, 'entrada', 30, 35, 65, 'compra', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY)),
(16, 2, 'salida', 1, 12, 11, 'venta', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY));


-- ═══════════════════════════════════════
-- 📋 TABLA 5: configuracion
-- ═══════════════════════════════════════
CREATE TABLE configuracion (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  clave         VARCHAR(100) NOT NULL UNIQUE,
  valor         TEXT NULL,
  tipo          ENUM('texto','numero','booleano','json') DEFAULT 'texto',
  descripcion   VARCHAR(255) NULL,
  updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos iniciales configuracion
INSERT INTO configuracion (clave, valor, tipo) VALUES
('nombre_negocio', 'Artículos Religiosos Jesús de Nazaret', 'texto'),
('direccion', 'Iguala de la Independencia, Guerrero', 'texto'),
('telefono', '', 'texto'),
('email', '', 'texto'),
('moneda', 'MXN', 'texto'),
('stock_minimo_global', '5', 'numero'),
('alertas_activas', '1', 'booleano'),
('email_alertas', '', 'texto'),
('iva_porcentaje', '16', 'numero'),
('envio_gratis_desde', '500', 'numero');


-- ═══════════════════════════════════════
-- 📋 TABLA 6: sesiones (para auth segura)
-- ═══════════════════════════════════════
CREATE TABLE sesiones (
  id          VARCHAR(128) PRIMARY KEY,   -- session token
  usuario_id  INT UNSIGNED NOT NULL,
  ip          VARCHAR(45)  NULL,
  user_agent  TEXT NULL,
  expires_at  DATETIME NOT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  INDEX idx_usuario  (usuario_id),
  INDEX idx_expires  (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ═══════════════════════════════════════
-- 📋 TABLAS FUTURAS (e-commerce)
-- ═══════════════════════════════════════

-- TABLA 7: clientes
CREATE TABLE clientes (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(150) NOT NULL,
  email         VARCHAR(150) NOT NULL UNIQUE,
  password      VARCHAR(255) NULL,
  telefono      VARCHAR(20)  NULL,
  direccion     TEXT NULL,
  ciudad        VARCHAR(100) NULL,
  estado_rep    VARCHAR(100) NULL,
  cp            VARCHAR(10)  NULL,
  estado        ENUM('activo','inactivo') DEFAULT 'activo',
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLA 8: pedidos
CREATE TABLE pedidos (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  folio           VARCHAR(20) NOT NULL UNIQUE,  -- PED-2024-001
  cliente_id      INT UNSIGNED NULL,
  usuario_id      INT UNSIGNED NULL,             -- quien procesó
  subtotal        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  descuento       DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  iva             DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  envio           DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  total           DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  estado          ENUM('pendiente','confirmado','en_proceso','enviado','entregado','cancelado') NOT NULL DEFAULT 'pendiente',
  metodo_pago     ENUM('efectivo','transferencia','tarjeta','otro') NULL,
  direccion_envio TEXT NULL,
  notas           TEXT NULL,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  FOREIGN KEY (cliente_id)  REFERENCES clientes(id)  ON DELETE SET NULL,
  FOREIGN KEY (usuario_id)  REFERENCES usuarios(id)  ON DELETE SET NULL,
  INDEX idx_folio   (folio),
  INDEX idx_estado  (estado),
  INDEX idx_cliente (cliente_id),
  INDEX idx_fecha   (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLA 9: pedido_detalle
CREATE TABLE pedido_detalle (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  pedido_id     INT UNSIGNED NOT NULL,
  producto_id   INT UNSIGNED NULL,
  nombre_prod   VARCHAR(200) NOT NULL,  -- snapshot del nombre
  sku           VARCHAR(50)  NOT NULL,  -- snapshot del SKU
  precio_unit   DECIMAL(10,2) NOT NULL,
  cantidad      INT NOT NULL DEFAULT 1,
  subtotal      DECIMAL(10,2) NOT NULL,
  
  FOREIGN KEY (pedido_id)   REFERENCES pedidos(id)   ON DELETE CASCADE,
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL,
  INDEX idx_pedido   (pedido_id),
  INDEX idx_producto (producto_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TABLA 10: resenas
CREATE TABLE resenas (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  producto_id   INT UNSIGNED NOT NULL,
  cliente_id    INT UNSIGNED NULL,
  nombre        VARCHAR(100) NOT NULL,
  calificacion  TINYINT NOT NULL DEFAULT 5,  -- 1 al 5
  comentario    TEXT NULL,
  estado        ENUM('pendiente','aprobado','rechazado') DEFAULT 'pendiente',
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  FOREIGN KEY (cliente_id)  REFERENCES clientes(id)  ON DELETE SET NULL,
  INDEX idx_producto (producto_id),
  INDEX idx_estado   (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ═══════════════════════════════════════
-- 🔧 VISTAS ÚTILES (VIEWs)
-- ═══════════════════════════════════════

-- VIEW 1: v_productos_completos
CREATE OR REPLACE VIEW v_productos_completos AS
SELECT 
  p.*,
  c.nombre AS nombre_categoria,
  CASE
    WHEN p.stock_actual = 0 THEN 'sin_stock'
    WHEN p.stock_actual <= p.stock_minimo THEN 'stock_bajo'
    ELSE 'ok'
  END AS stock_status
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id;

-- VIEW 2: v_alertas_stock
CREATE OR REPLACE VIEW v_alertas_stock AS
SELECT 
  p.nombre,
  p.sku,
  c.nombre AS categoria,
  p.stock_actual,
  p.stock_minimo,
  (p.stock_minimo - p.stock_actual) AS diferencia
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id
WHERE p.stock_actual <= p.stock_minimo;

-- VIEW 3: v_movimientos_completos
CREATE OR REPLACE VIEW v_movimientos_completos AS
SELECT 
  m.*,
  p.nombre AS nombre_producto,
  p.sku,
  u.nombre AS nombre_usuario
FROM movimientos_inventario m
LEFT JOIN productos p ON m.producto_id = p.id
LEFT JOIN usuarios u ON m.usuario_id = u.id;

-- VIEW 4: v_dashboard_stats
CREATE OR REPLACE VIEW v_dashboard_stats AS
SELECT
  (SELECT COUNT(*) FROM productos WHERE estado = 'activo') AS total_productos,
  (SELECT COUNT(*) FROM categorias WHERE estado = 'activo') AS total_categorias,
  (SELECT COUNT(*) FROM productos WHERE stock_actual <= stock_minimo AND stock_actual > 0) AS productos_stock_bajo,
  (SELECT COUNT(*) FROM productos WHERE stock_actual = 0) AS productos_sin_stock,
  (SELECT IFNULL(SUM(stock_actual * precio_venta), 0) FROM productos WHERE estado != 'inactivo') AS valor_inventario,
  (SELECT IFNULL(SUM(stock_actual * precio_costo), 0) FROM productos WHERE estado != 'inactivo') AS valor_costo;


-- ═══════════════════════════════════════
-- 🔒 SEGURIDAD FINAL
-- ═══════════════════════════════════════
-- Reactivar verificación de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;
