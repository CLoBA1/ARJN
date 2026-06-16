<?php
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