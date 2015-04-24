<?php
header("Access-Control-Allow-Origin: *");
header("Content-type: application/json");
session_name('Global');
session_id('TEST');
session_start();

// Make the array to hold the peers and files
if (!array_key_exists("files", $_SESSION)) {
	$_SESSION["peers"] = [];
	$_SESSION["files"] = [];
}

$action = $_GET["action"];

if ($action == "set_peer") {
	$peerid = $_GET["peerid"];
	$_SESSION["peers"][$peerid] = 1;
} else if ($action == "remove_peer") {
	$peerid = $_GET["peerid"];
	unset($_SESSION["peers"][$peerid]);
} else if ($action == "get_peers") {
	$keys = array_keys($_SESSION["peers"]);
	echo json_encode($keys);
} else if ($action == "get_file") {
	// Get the peerid and file
	$peerid = $_GET["peerid"];
	$file = $_GET["file"];

	// Save it in the session
	$_SESSION["files"][$peerid] = $file;

	// Show all the peers and files
	echo json_encode($_SESSION["files"]);
} else if ($action == "clear") {
	// Reset the files
	$_SESSION["peers"] = [];
	$_SESSION["files"] = [];
}

session_write_close();
?>

