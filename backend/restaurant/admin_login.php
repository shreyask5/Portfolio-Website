<?php
session_start();

// Database connection
$host = 'portfolio-website-database.chc6icogsvaz.ap-south-1.rds.amazonaws.com';
$db = 'waitlist_db';
$user = 'admin';
$password = 'shreyasksh5';
$port = 3306;

$conn = new mysqli($host, $user, $password, $db, $port);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to sanitize input
function test_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = test_input($_POST["username"]);
    $password = test_input($_POST["password"]);

    // Prepare and execute query to fetch users
    $stmt = $conn->prepare("SELECT * FROM Admin");
    if (!$stmt) {
        die("Prepare failed: " . $conn->error);
    }

    if (!$stmt->execute()) {
        die("Execute failed: " . $stmt->error);
    }

    $result = $stmt->get_result();
    $users = $result->fetch_all(MYSQLI_ASSOC);

    // Iterate through users to validate login credentials
    foreach ($users as $user) {
        if ($user['username'] == $username && $user['password'] == $password) {
            // Successful login
            $_SESSION['admin_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            header("Location: adminpage.php");
            exit();
        }
    }

    // If no match found, show alert
    echo "<script language='javascript'>";
    echo "alert('WRONG INFORMATION')";
    echo "</script>";
}

// Close the connection
$stmt->close();
$conn->close();
?>
