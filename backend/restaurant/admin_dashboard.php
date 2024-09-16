<?php
// Start session handling
session_start();

// Check if the admin is logged in, if not, redirect to login page
if (!isset($_SESSION['admin_id'])) {
    header("Location: admin_login.html");
    exit();
}

// Display the admin dashboard with a welcome message
echo "<h1>Welcome, " . $_SESSION['username'] . "!</h1>";
echo "<p>You are now logged in to the admin dashboard.</p>";
?>
