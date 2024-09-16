<?php

$conn = "";

try {
    $host = 'portfolio-website-database.chc6icogsvaz.ap-south-1.rds.amazonaws.com';
    $db = 'waitlist_db';
    $user = 'admin';
    $password = 'shreyasksh5';
    $port = 3306;    

	$conn = new PDO(
		"mysql:host=$servername; dbname=waitlist_db",
		$username, $password
	);
	
$conn->setAttribute(PDO::ATTR_ERRMODE,
					PDO::ERRMODE_EXCEPTION);
}
catch(PDOException $e) {
	echo "Connection failed: " . $e->getMessage();
}

?>