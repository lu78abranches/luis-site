O e-mail está sendo enviado com sucesso (chega na minha caixa de entrada), mas o evento `clique_email` não está disparando no Analytics. Suspeito que um erro/aviso do PHP relacionado à falha de gravação no banco (esperada nesse ambiente local, já que a conexão remota ao MySQL da Hostinger costuma ser bloqueada) esteja sendo impresso na resposta HTTP, quebrando o JSON antes dele chegar ao JavaScript.

## O que corrigir no `salvar-lead.php`

1. Garanta que qualquer erro relacionado à gravação no banco fique contido — nunca deixe um `echo`, `var_dump`, warning ou notice do PHP vazar para a saída da resposta. Use `error_log()` para registrar o erro internamente, não a saída padrão.

2. No topo do script (ou antes de qualquer tentativa de conexão com o banco), desative a exibição de erros na resposta:
```php
ini_set('display_errors', '0');
error_reporting(E_ALL); // continua registrando no log, só não exibe na resposta
```

3. Envolva a etapa de gravação no banco em try/catch isolado, sem deixar a exceção propagar pra fora do script:
```php
$salvo_no_banco = false;
try {
    // tentativa de conexão e insert no banco
    $salvo_no_banco = true;
} catch (Throwable $e) {
    error_log('Falha ao salvar lead no banco: ' . $e->getMessage());
    $salvo_no_banco = false;
}
```

4. Garanta que, independente do resultado do banco, o script sempre termine devolvendo um JSON limpo e válido, como único conteúdo da resposta:
```php
header('Content-Type: application/json');
echo json_encode([
    'mensagem_enviada' => $mensagem_enviada,
    'salvo_no_banco' => $salvo_no_banco
]);
exit;
```

## Como validar
Depois do ajuste, teste o envio por e-mail de novo com o DevTools aberto (aba Network) e confirme que a resposta do `salvar-lead.php` é só o JSON, sem nenhum texto de erro/aviso antes ou depois. Confirme também que o evento `clique_email` aparece no GA4 DebugView nesse teste.
