<?php
session_start();

// Check if the admin is logged in
if (!isset($_SESSION['admin_id'])) {
    header("Location: index.php");
    exit();
}

// Display the welcome message
echo "<h1>Welcome, " . htmlspecialchars($_SESSION['username']) . "!</h1>";
echo "<p>You are now logged in to the admin dashboard.</p>";
?>



<h2>Hello Admin</h2>
<p>Welcome to the admin dashboard.</p>