Quero reorganizar a estrutura de pastas do projeto, que hoje está tudo solto num diretório único. Segue a estrutura alvo, tarefas e critérios de aceitação.

## Estrutura de pastas alvo (proposta)

```
/
├── public/
│   ├── index.html
│   ├── deployed.html
│   ├── politica-privacidade.html
│   └── README.md
│
├── assets/
│   ├── css/
│   │   ├── style.css
│   │   ├── deployed_style.css
│   │   └── reset.css
│   ├── js/
│   │   └── lead-widget.js
│   └── img/
│       └── (todas as imagens do projeto)
│
├── backend/
│   ├── salvar-lead.php
│   └── create_leads_table.sql
│
├── config/
│   └── config.sample.php
│
├── docs/
│   └── (arquivos prompt-*.md e documentação)
│
└── scripts-dev/
        └── (ferramentas de desenvolvimento e scripts de manutenção)
```

## Tarefas

1. Extrair o JavaScript do `lead-widget` (está inline em `index.html` e `deployed.html`) para `assets/js/lead-widget.js` e referenciar por `<script src="/assets/js/lead-widget.js"></script>` nos HTMLs.

2. Mover os arquivos CSS para `assets/css/` e atualizar as tags `<link>` nos HTMLs.

3. Mover imagens para `assets/img/` e atualizar todos os `src` e `url()` no CSS.

4. Mover `salvar-lead.php` e `create_leads_table.sql` para `backend/` e ajustar o `fetch()`/`form action` para `/backend/salvar-lead.php` (ou usar `/api/salvar-lead.php` com rewrite).

5. Mover `prompt-*.md` para `docs/`.

6. Mover scripts de manutenção para `scripts-dev/`.

7. Atualizar `README.md` com instruções de dev e deploy (como servir `public/` localmente e onde colocar `config/config.php`).

8. Criar `config/config.sample.php` e adicionar `config/config.php` ao `.gitignore`.

## Testes e verificação

    - Todas as páginas carregam sem 404.
    - CSS e imagens aplicados corretamente.
    - Lead-widget envia requests para o endpoint correto e recebe JSON limpo.


```powershell
# Servir a pasta public como docroot
php -S localhost:8000 -t public

# Testar endpoint
curl.exe -X POST http://localhost:8000/backend/salvar-lead.php -d "nome=Teste&email=test@example.com&mensagem=ola"
```

## Critérios de aceitação


## Observações


Quer que eu continue e mova também os CSS e imagens agora, criando o branch `reorg/directories` e committando as mudanças?
Quer que eu aplique as mudanças automaticamente (mover arquivos e ajustar paths) e crie o branch `reorg/directories` com os commits, ou prefere receber o patch para revisar antes de aplicar?
