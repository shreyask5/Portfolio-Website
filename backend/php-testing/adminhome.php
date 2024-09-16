<?php
session_start();

// Check if user is logged in
if (!isset($_SESSION["username"])) {
    header("Location: login.php");
    exit();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Admin Home Page</title>
</head>
<body>

<h1>THIS IS ADMIN HOME PAGE</h1>
<p>Welcome, <?php echo htmlspecialchars($_SESSION["username"], ENT_QUOTES); ?></p>

<a href="logout.php">Logout</a>

</body>
</html>
