<?php
header('Content-Type: application/json; charset=utf-8');

function jsonResponse(bool $success, string $message): void {
    echo json_encode(['sucesso' => $success, 'mensagem' => $message], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonResponse(false, 'Método inválido.');
}

$nome = trim($_POST['nome'] ?? '');
$telefone = trim($_POST['telefone'] ?? '');
$email = trim($_POST['email'] ?? '');
$mensagem = trim($_POST['mensagem'] ?? '');
$canal = trim($_POST['canal'] ?? 'formulario');
$pagina_origem = trim($_POST['pagina_origem'] ?? '');
$consentimento = $_POST['consentimento_lgpd'] ?? '';
$campo_extra = trim($_POST['campo_extra'] ?? '');

// Honeypot anti-spam
if ($campo_extra !== '') {
    jsonResponse(true, 'OK');
}

if ($nome === '') {
    jsonResponse(false, 'Nome é obrigatório.');
}

$canal = in_array($canal, ['whatsapp', 'email', 'formulario'], true) ? $canal : 'formulario';

$consentimentoLGPD = filter_var($consentimento, FILTER_VALIDATE_BOOLEAN, FILTER_NULL_ON_FAILURE);
if ($consentimentoLGPD !== true) {
    jsonResponse(false, 'É necessário aceitar a política de privacidade.');
}

if ($canal === 'email') {
    if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        jsonResponse(false, 'E-mail válido é obrigatório para contato por e-mail.');
    }
}

$dbHost = 'localhost';
$dbName = 'database';
$dbUser = 'user';
$dbPass = 'password';

try {
    $pdo = new PDO(
        "mysql:host={$dbHost};dbname={$dbName};charset=utf8mb4",
        $dbUser,
        $dbPass,
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
} catch (PDOException $exception) {
    jsonResponse(false, 'Erro ao conectar com o banco de dados.');
}

try {
    $stmt = $pdo->prepare(
        'INSERT INTO leads (nome, telefone, email, mensagem, canal, pagina_origem, consentimento_lgpd) VALUES (:nome, :telefone, :email, :mensagem, :canal, :pagina_origem, :consentimento_lgpd)'
    );
    $stmt->execute([
        ':nome' => $nome,
        ':telefone' => $telefone !== '' ? $telefone : null,
        ':email' => $email !== '' ? $email : null,
        ':mensagem' => $mensagem !== '' ? $mensagem : null,
        ':canal' => $canal,
        ':pagina_origem' => $pagina_origem !== '' ? $pagina_origem : null,
        ':consentimento_lgpd' => $consentimentoLGPD ? 1 : 0,
    ]);
} catch (PDOException $exception) {
    jsonResponse(false, 'Erro ao salvar o lead.');
}

if ($canal === 'email') {
    $smtpHost = 'smtp.hostinger.com';
    $smtpUser = 'seuusuario@seudominio.com';
    $smtpPass = 'SUA_SENHA_SMTP';
    $smtpPort = 587;
    $smtpSecure = 'tls';
    $destino = 'luisabranches.violao@gmail.com';
    $assunto = 'Novo lead por e-mail - Aulas de Violão';

    if (!loadPHPMailer()) {
        jsonResponse(false, 'PHPMailer não encontrado. Instale a biblioteca PHPMailer no servidor.');
    }

    $mail = new PHPMailer\PHPMailer\PHPMailer(true);
    try {
        $mail->isSMTP();
        $mail->Host = $smtpHost;
        $mail->SMTPAuth = true;
        $mail->Username = $smtpUser;
        $mail->Password = $smtpPass;
        $mail->SMTPSecure = $smtpSecure;
        $mail->Port = $smtpPort;
        $mail->CharSet = 'UTF-8';

        $mail->setFrom($smtpUser, 'Contato Aulas de Violão');
        $mail->addAddress($destino, 'Luis Abranches');
        $mail->addReplyTo($email, $nome);
        $mail->Subject = $assunto;
        $mail->isHTML(true);

        $bodyHtml = '<p>Novo lead recebido pelo site:</p>' .
            '<ul>' .
            '<li><strong>Nome:</strong> ' . htmlspecialchars($nome, ENT_QUOTES, 'UTF-8') . '</li>' .
            '<li><strong>Telefone:</strong> ' . htmlspecialchars($telefone, ENT_QUOTES, 'UTF-8') . '</li>' .
            '<li><strong>E-mail:</strong> ' . htmlspecialchars($email, ENT_QUOTES, 'UTF-8') . '</li>' .
            '<li><strong>Canal:</strong> ' . htmlspecialchars($canal, ENT_QUOTES, 'UTF-8') . '</li>' .
            '<li><strong>Página de origem:</strong> ' . htmlspecialchars($pagina_origem, ENT_QUOTES, 'UTF-8') . '</li>' .
            '<li><strong>Mensagem:</strong><br>' . nl2br(htmlspecialchars($mensagem, ENT_QUOTES, 'UTF-8')) . '</li>' .
            '</ul>';

        $mail->Body = $bodyHtml;
        $mail->AltBody = "Novo lead recebido:\nNome: {$nome}\nTelefone: {$telefone}\nE-mail: {$email}\nCanal: {$canal}\nPágina de origem: {$pagina_origem}\nMensagem: {$mensagem}";

        $mail->send();
    } catch (Exception $e) {
        jsonResponse(false, 'Erro ao enviar o e-mail de notificação.');
    }
}

jsonResponse(true, 'Lead salvo com sucesso.');

function loadPHPMailer(): bool {
    $base = __DIR__ . '/vendor/phpmailer/phpmailer/src';
    $files = ['PHPMailer.php', 'SMTP.php', 'Exception.php'];
    foreach ($files as $file) {
        $path = $base . '/' . $file;
        if (!file_exists($path)) {
            return false;
        }
        require_once $path;
    }
    return class_exists('PHPMailer\\PHPMailer\\PHPMailer');
}
