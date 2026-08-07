<?php
/**
 * Carrega variáveis de um arquivo .env para o ambiente PHP.
 * Sem dependências externas — não precisa de Composer.
 */
function carregarEnv(string $caminho): void
{
    if (!file_exists($caminho)) {
        return;
    }

    $linhas = file($caminho, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($linhas as $linha) {
        $linha = trim($linha);

        if ($linha === '' || str_starts_with($linha, '#')) {
            continue;
        }

        [$chave, $valor] = array_pad(explode('=', $linha, 2), 2, '');
        $chave = trim($chave);
        $valor = trim($valor, " \t\n\r\0\x0B\"'");

        if ($chave !== '') {
            putenv("{$chave}={$valor}");
            $_ENV[$chave] = $valor;
        }
    }
}

carregarEnv(__DIR__ . '/.env');
