<?php

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

ini_set('display_errors', 1);
error_reporting(E_ALL);

function log_message($message) {
    file_put_contents('debug_log.txt', date('Y-m-d H:i:s') . ': ' . $message . "\n", FILE_APPEND);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['error' => 'Only POST requests are allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$code = isset($input['code']) ? $input['code'] : '';

if (empty($code)) {
    echo json_encode(['error' => 'No code provided']);
    exit;
}

$tempFile = tempnam(sys_get_temp_dir(), 'code_');
file_put_contents($tempFile, $code);

log_message("Temporary file created: " . $tempFile);
log_message("Code length: " . strlen($code));

$pythonScript = __DIR__ . '/language_identifier.py';

if (!file_exists($pythonScript)) {
    log_message("Python script not found at: " . $pythonScript);
    echo json_encode(['error' => 'Python script not found']);
    unlink($tempFile);
    exit;
}

$command = "python \"$pythonScript\" \"$tempFile\" 2>&1";
log_message("Executing command: " . $command);

$output = [];
$returnValue = 0;
exec($command, $output, $returnValue);


unlink($tempFile);


if ($returnValue !== 0) {
    log_message("Python script execution failed with return code: " . $returnValue);
    log_message("Output: " . print_r($output, true));
    echo json_encode(['error' => 'Failed to execute Python script', 'details' => implode("\n", $output)]);
    exit;
}


$jsonOutput = implode("\n", $output);
log_message("Python output: " . $jsonOutput);


$decodedOutput = json_decode($jsonOutput, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    log_message("JSON decode error: " . json_last_error_msg());
    echo json_encode(['error' => 'Invalid JSON returned from Python script', 'raw_output' => $jsonOutput]);
    exit;
}


echo $jsonOutput;
?>