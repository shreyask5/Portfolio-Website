<?php
session_start();

// Database connection
$host = 'localhost';
$db = 'waitlist_db';
$user = 'root';
$password = '';

$conn = new mysqli($host, $user, $password, $db);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Fetch admin data from the database
    $stmt = $conn->prepare("SELECT * FROM Admin WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    $admin = $result->fetch_assoc();

    // Check if the admin exists and password matches
    if ($admin && password_verify($password, $admin['password_hash'])) {
        // Login successful
        $_SESSION['admin_id'] = $admin['id'];
        $_SESSION['username'] = $admin['username'];
        header("Location: admin_dashboard.php");
    } else {
        // Login failed
        echo "<p>Invalid username or password.</p>";
    }
    $stmt->close();
}
$conn->close();
?>
