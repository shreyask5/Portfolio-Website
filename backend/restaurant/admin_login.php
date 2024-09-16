<?php
session_start();

// Database connection parameters
$host = 'portfolio-website-database.chc6icogsvaz.ap-south-1.rds.amazonaws.com';
$db = 'waitlist_db';
$user = 'admin';
$password = 'shreyasksh5';
$port = 3306;

// Create connection and add error handling
$conn = new mysqli($host, $user, $password, $db, $port);

// Check if connection is successful
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Check if form fields are set
    if (isset($_POST['username']) && isset($_POST['password'])) {
        $username = $_POST['username'];
        $password = $_POST['password'];

        // Validate input length to avoid SQL injection attempts
        if (strlen($username) > 50 || strlen($password) > 50) {
            die("Invalid input length.");
        }

        // Prepare the statement
        $stmt = $conn->prepare("SELECT * FROM Admin WHERE username = ?");
        if (!$stmt) {
            die("Prepare failed: " . $conn->error);
        }

        // Bind parameters and execute
        $stmt->bind_param("s", $username);
        if (!$stmt->execute()) {
            die("Execute failed: " . $stmt->error);
        }

        // Get the result
        $result = $stmt->get_result();
        if ($result === false) {
            die("Get result failed: " . $stmt->error);
        }

        // Fetch admin data
        $admin = $result->fetch_assoc();
        
        // Check if admin exists and verify password
        if ($admin && password_verify($password, $admin['password_hash'])) {
            // Successful login
            $_SESSION['admin_id'] = $admin['id'];
            $_SESSION['username'] = $admin['username'];
            header("Location: admin_dashboard.php");
            exit();
        } else {
            // Login failed
            echo "<p>Invalid username or password.</p>";
        }

        // Close the statement and result
        $stmt->close();
    } else {
        echo "<p>Please fill out both fields.</p>";
    }
} else {
    echo "<p>Invalid request method.</p>";
}

// Close the connection
$conn->close();
?>
