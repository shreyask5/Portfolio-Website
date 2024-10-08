<?php

$host = 'portfolio-website-database.chc6icogsvaz.ap-south-1.rds.amazonaws.com';
$db = 'waitlist_db';
$user = 'admin';
$password = 'shreyasksh5';
$port = 3306;  

ob_start();
session_start();

$data = new mysqli($host, $user, $password, $db);

if ($data->connect_error) {
    die("Connection error: " . $data->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST["username"];
    $password = $_POST["password"];

    $sql = "SELECT * FROM Admin WHERE username = ?";
    $stmt = $data->prepare($sql);
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();
    if ($row) {
        if (password_verify($password, $row['password_hash'])) {
            session_regenerate_id(true);
            $_SESSION["username"] = $username;
            header("Location: adminhome.php");
            exit;
            ob_end_flush();
        } else {
            echo "Invalid username or password.";
        }
    } else {
        echo "Invalid username or password. No Row";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Login Form</title>
</head>
<body>
    <center>
        <h1>Login Form</h1>
        <br><br><br><br>
        <div style="background-color: grey; width: 500px;">
            <br><br>
            <form action="index.php" method="POST">
                <div>
                    <label>Username</label>
                    <input type="text" name="username" value="<?php echo htmlspecialchars($_POST['username'] ?? '', ENT_QUOTES); ?>" required>
                </div>
                <br><br>
                <div>
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <br><br>
                <div>
                    <input type="submit" value="Login">
                </div>
            </form>
            <br><br>
        </div>
    </center>
</body>
</html>
