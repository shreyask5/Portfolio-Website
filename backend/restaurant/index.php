<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Admin Login</title>
    <link rel="stylesheet" href="restaurant.css">
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="icon" href="https://my-portfolio-website-s3-bucket.s3.ap-south-1.amazonaws.com/assets/SK+Site+Favicon.png" type="image/x-icon" class="favcion">
    <link
      href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700;900&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <h2>Admin Login</h2>
            <form action="admin_login.php" method="POST">
                <div class="input-group">
                    <label for="username">Username:</label>
                    <input class="input-text" type="text" id="username" name="username" placeholder="Enter your username" required>
                </div>
                <div class="input-group">
                    <label for="password">Password:</label>
                    <input class="input-text" type="password" id="password" name="password" placeholder="Enter your password" required>
                </div>
                <button class="btn btn--med" type="submit">Login</button>
            </form>
        </div>
    </div>
</body>
</html>
