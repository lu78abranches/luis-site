<?php
header('Content-Type: application/json; charset=utf-8');

// Do not display PHP errors in the HTTP response; always log them instead.
ini_set('display_errors', '0');
error_reporting(E_ALL);

// Convert PHP errors into logged entries and prevent them from being displayed.
set_error_handler(function ($errno, $errstr, $errfile, $errline) {
    error_log(sprintf("PHP error [%d] %s in %s on line %d", $errno, $errstr, $errfile, $errline));
    return true; // mark as handled so PHP won't output it
});

// Handle uncaught exceptions: log and return a minimal JSON response.
set_exception_handler(function ($e) {
    error_log('Uncaught exception: ' . $e->getMessage());
    if (!headers_sent()) {
        header('Content-Type: application/json; charset=utf-8');
    }
    echo json_encode(['sucesso' => false, 'mensagem' => 'Ocorreu um erro interno.'], JSON_UNESCAPED_UNICODE);
    exit;
});

// Catch fatal shutdown errors and log them (attempt to return JSON if possible).
register_shutdown_function(function () {
    $err = error_get_last();
    if ($err && in_array($err['type'], [E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR], true)) {
        error_log('Fatal error: ' . json_encode($err));
        if (!headers_sent()) {
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['sucesso' => false, 'mensagem' => 'Ocorreu um erro interno.'], JSON_UNESCAPED_UNICODE);
        }
    }
});

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
    error_log('Falha ao conectar ao banco de dados: ' . $exception->getMessage());
    $erroBanco = 'Erro ao conectar com o banco de dados.';
    // keep technical details for internal notification only
    $erroBancoDetalhes = $exception->getMessage();
    $pdo = null;
}

if (!isset($erroBanco)) {
    $erroBanco = null;
}
$erroBancoDetalhes = $erroBancoDetalhes ?? null;
$salvoNoBanco = false;
if ($pdo !== null) {
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
        $salvoNoBanco = true;
    } catch (PDOException $exception) {
        error_log('Falha ao salvar lead no banco: ' . $exception->getMessage());
        $erroBanco = 'Erro ao salvar lead no banco de dados.';
        // keep technical details for internal notification only
        $erroBancoDetalhes = $exception->getMessage();
    }
}

function sendNotificationEmail(string $subject, string $bodyHtml, string $bodyText, string $replyName = '', string $replyEmail = ''): bool {
    if (!loadPHPMailer()) {
        return false;
    }

    $smtpHost = 'smtp.hostinger.com';
    $smtpUser = 'seuusuario@seudominio.com';
    $smtpPass = 'SUA_SENHA_SMTP';
    $smtpPort = 587;
    $smtpSecure = 'tls';
    $destino = 'luisabranches.violao@gmail.com';

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
        if ($replyEmail !== '') {
            $mail->addReplyTo($replyEmail, $replyName ?: 'Contato');
        }
        $mail->Subject = $subject;
        $mail->isHTML(true);
        $mail->Body = $bodyHtml;
        $mail->AltBody = $bodyText;
        $mail->send();
        return true;
    } catch (\Exception $e) {
        error_log('PHPMailer error: ' . $e->getMessage());
        return false;
    }
}

$mensagemEnviada = false;
$notificacaoDeErro = false;

if ($canal === 'email') {
    $assunto = 'Novo lead por e-mail - Aulas de Violão';
    $bodyHtml = '<p>Novo lead recebido pelo site:</p>' .
        '<ul>' .
        '<li><strong>Nome:</strong> ' . htmlspecialchars($nome, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Telefone:</strong> ' . htmlspecialchars($telefone, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>E-mail:</strong> ' . htmlspecialchars($email, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Canal:</strong> ' . htmlspecialchars($canal, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Página de origem:</strong> ' . htmlspecialchars($pagina_origem, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Mensagem:</strong><br>' . nl2br(htmlspecialchars($mensagem, ENT_QUOTES, 'UTF-8')) . '</li>' .
        '</ul>';
    $bodyText = "Novo lead recebido:\nNome: {$nome}\nTelefone: {$telefone}\nE-mail: {$email}\nCanal: {$canal}\nPágina de origem: {$pagina_origem}\nMensagem: {$mensagem}";
    $mensagemEnviada = sendNotificationEmail($assunto, $bodyHtml, $bodyText, $nome, $email);
}

if ($erroBanco !== null) {
    $avisoBodyHtml = '<p>Falha ao salvar lead no banco de dados. Dados recebidos:</p>' .
        '<ul>' .
        '<li><strong>Nome:</strong> ' . htmlspecialchars($nome, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Telefone:</strong> ' . htmlspecialchars($telefone, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>E-mail:</strong> ' . htmlspecialchars($email, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Canal:</strong> ' . htmlspecialchars($canal, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Página de origem:</strong> ' . htmlspecialchars($pagina_origem, ENT_QUOTES, 'UTF-8') . '</li>' .
        '<li><strong>Mensagem:</strong><br>' . nl2br(htmlspecialchars($mensagem, ENT_QUOTES, 'UTF-8')) . '</li>' .
        '<li><strong>Erro do banco (resumo):</strong> ' . htmlspecialchars($erroBanco, ENT_QUOTES, 'UTF-8') . '</li>' .
        '</ul>';
    // Append technical details to the internal notification only
    if (!empty($erroBancoDetalhes)) {
        $avisoBodyHtml .= '<h3>Detalhes técnicos</h3><pre style="white-space:pre-wrap;">' . htmlspecialchars($erroBancoDetalhes, ENT_QUOTES, 'UTF-8') . '</pre>';
        $avisoBodyText = "Falha ao salvar lead no banco de dados. Dados recebidos:\nNome: {$nome}\nTelefone: {$telefone}\nE-mail: {$email}\nCanal: {$canal}\nPágina de origem: {$pagina_origem}\nMensagem: {$mensagem}\nErro do banco: {$erroBanco}\nDetalhes técnicos: {$erroBancoDetalhes}";
    } else {
        $avisoBodyText = "Falha ao salvar lead no banco de dados. Dados recebidos:\nNome: {$nome}\nTelefone: {$telefone}\nE-mail: {$email}\nCanal: {$canal}\nPágina de origem: {$pagina_origem}\nMensagem: {$mensagem}\nErro do banco: {$erroBanco}";
    }
    $notificacaoDeErro = sendNotificationEmail('Falha ao salvar lead — dados abaixo', $avisoBodyHtml, $avisoBodyText, $nome, $email);
}

$jsonData = [
    'mensagem_enviada' => $mensagemEnviada,
    'salvo_no_banco' => $salvoNoBanco,
    'notificacao_erro' => $notificacaoDeErro,
    'sucesso' => true,
    'mensagem' => 'Sua solicitação foi recebida. Entraremos em contato em breve.'
];

echo json_encode($jsonData, JSON_UNESCAPED_UNICODE);
exit;

function loadPHPMailer(): bool {
    $base = __DIR__ . '/vendor/phpmailer/phpmailer/src';
    $files = ['PHPMailer.php', 'SMTP.php', 'Exception.php'];
    foreach ($files as $file) {
        $path = $base . '/' . $file;
        if (!file_exists($path)) {
            error_log('PHPMailer missing file: ' . $path);
            return false;
        }
        require_once $path;
    }
    return class_exists('PHPMailer\\PHPMailer\\PHPMailer');
}
