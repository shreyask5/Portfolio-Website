<?php
// Database connection
$host = 'portfolio-website-database.chc6icogsvaz.ap-south-1.rds.amazonaws.com';  // RDS endpoint
$db = 'waitlist_db';  // Database name on RDS
$user = 'admin';      // Username for RDS instance
$password = 'shreyasksh5';  // Password for RDS instance
$port = 3306;         // MySQL port, default is 3306


$conn = new mysqli($host, $user, $password, $db);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} else {
    echo "Connected to database successfully.\n";
}

// Hash password and insert into the database
$username = 'admin'; // Set the username to 'admin'
$password = 'admin'; // Set the password to 'admin'
$password_hash = password_hash($password, PASSWORD_DEFAULT); // Hash the password

// Prepare and bind the query
$stmt = $conn->prepare("INSERT INTO Admin (username, password_hash) VALUES (?, ?)");
if ($stmt === false) {
    die("Error in preparing statement: " . $conn->error);
}

// Bind the parameters
$stmt->bind_param("ss", $username, $password_hash);

// Execute the statement and check for errors
if ($stmt->execute()) {
    echo "Admin account created successfully!\n";
} else {
    echo "Error: " . $stmt->error . "\n";
}

$stmt->close();
$conn->close();
?>
