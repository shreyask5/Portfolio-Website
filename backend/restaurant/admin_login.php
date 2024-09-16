<?php
// Start output buffering to prevent header issues
ob_start(); 

// Start session handling
session_start();

// Enable error reporting for debugging
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Database connection details
$host = 'portfolio-website-database.chc6icogsvaz.ap-south-1.rds.amazonaws.com';
$db = 'waitlist_db';
$user = 'admin';
$password = 'shreyasksh5';
$port = 3306; // MySQL default port

// Establish connection to the database
$conn = new mysqli($host, $user, $password, $db);

// Check database connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Debugging: Print submitted values
    $username = test_input($_POST['username']);
    $password = test_input($_POST['password']);
    echo "Username: $username, Password: $password <br>"; // Debugging
    
    // Prepare and execute query to fetch the admin data
    $stmt = $conn->prepare("SELECT * FROM Admin WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    $admin = $result->fetch_assoc();

    // Debugging: Print fetched admin details
    print_r($admin);

    // Check if admin exists and password matches
    if ($admin && password_verify($password, $admin['password_hash'])) {
        // Set session variables on successful login
        $_SESSION['admin_id'] = $admin['id'];
        $_SESSION['username'] = $admin['username'];
        echo "Login successful!"; // Debugging

        // Redirect to the admin dashboard
        header("Location: admin_dashboard.php");
        exit(); // Ensure the script stops after redirection
    } else {
        // Login failed
        echo "<p>Invalid username or password.</p>";
    }

    $stmt->close();
}

$conn->close();

// Sanitize input to prevent injection
function test_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

// End output buffering and send output
ob_end_flush();
?>
