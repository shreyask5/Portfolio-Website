<?php
// Database connection
$host = 'localhost';  // or your database host (default is localhost)
$db = 'waitlist_db';  // your database name
$user = 'root';       // your MySQL username (or any other MySQL user with privileges)
$password = '1234';       // your MySQL password

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
