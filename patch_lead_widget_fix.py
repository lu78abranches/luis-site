from pathlib import Path
import re

widget_html = '''    <!-- Barra fixa de captura de lead -->
    <div class="lead-widget lead-widget-hidden" id="lead-widget" aria-live="polite" aria-hidden="true">
      <div class="lead-widget-inner">
        <div class="lead-widget-header">
          <div>
            <strong>Agende sua aula</strong>
            <p>Rápido, seguro e sem bloquear sua navegação.</p>
          </div>
          <button type="button" id="lead-widget-close" class="lead-widget-close" aria-label="Fechar barra de contato">×</button>
        </div>
        <form id="lead-widget-form" class="lead-widget-form">
          <input type="hidden" name="canal" id="lead-widget-canal" value="formulario">
          <input type="hidden" name="pagina_origem" id="lead-widget-pagina_origem" value="home">
          <div class="lead-widget-row">
            <label for="lead-nome">Nome *</label>
            <input type="text" id="lead-nome" name="nome" required autocomplete="name">
          </div>
          <div class="lead-widget-row">
            <label for="lead-telefone">Telefone</label>
            <input type="tel" id="lead-telefone" name="telefone" autocomplete="tel">
          </div>
          <div class="lead-widget-row">
            <label for="lead-email">E-mail</label>
            <input type="email" id="lead-email" name="email" autocomplete="email">
          </div>
          <div class="lead-widget-row">
            <label for="lead-mensagem">Mensagem</label>
            <textarea id="lead-mensagem" name="mensagem" rows="2">Olá, gostaria de marcar uma aula experimental de violão!</textarea>
          </div>
          <div class="lead-widget-consent">
            <input type="checkbox" id="lead-consentimento" name="consentimento_lgpd" value="true">
            <label for="lead-consentimento">Li e concordo com a <a href="politica-privacidade.html" target="_blank" rel="noopener">política de privacidade</a></label>
          </div>
          <div class="lead-widget-actions">
            <button type="button" class="lead-widget-action" data-acao="whatsapp">Falar no WhatsApp</button>
            <button type="button" class="lead-widget-action" data-acao="email">Enviar e-mail</button>
          </div>
          <input type="text" name="campo_extra" class="lead-widget-honeypot" autocomplete="off" tabindex="-1">
          <div id="lead-widget-status" class="lead-widget-status"></div>
        </form>
      </div>
    </div>\n\n    <script>\n      (function() {\n        var STORAGE_KEY_CLOSED = 'luis_lead_widget_closed';\n        var leadWidget = document.getElementById('lead-widget');\n        var leadForm = document.getElementById('lead-widget-form');\n        var btnClose = document.getElementById('lead-widget-close');\n        var status = document.getElementById('lead-widget-status');\n        var canalInput = document.getElementById('lead-widget-canal');\n        var paginaOrigemInput = document.getElementById('lead-widget-pagina_origem');\n        var botaoAcoes = document.querySelectorAll('.lead-widget-action');\n        var contatoTriggers = document.querySelectorAll('.js-contact-trigger');\n        var formFields = {\n          nome: document.getElementById('lead-nome'),\n          telefone: document.getElementById('lead-telefone'),\n          email: document.getElementById('lead-email'),\n          mensagem: document.getElementById('lead-mensagem'),\n          consentimento: document.getElementById('lead-consentimento')\n        };\n\n        function setStatus(text, isError) {\n          status.textContent = text;\n          status.style.color = isError ? '#c72' : '#1a5';\n        }\n\n        function hideWidget() {\n          if (!leadWidget) return;\n          leadWidget.classList.add('lead-widget-hidden');\n          leadWidget.setAttribute('aria-hidden', 'true');\n        }\n\n        function showWidget() {\n          if (!leadWidget) return;\n          if (sessionStorage.getItem(STORAGE_KEY_CLOSED) === '1') {\n            hideWidget();\n            return;\n          }\n          leadWidget.classList.remove('lead-widget-hidden');\n          leadWidget.setAttribute('aria-hidden', 'false');\n        }\n\n        function openWidgetFor(canal, contexto) {\n          if (!canalInput) return;\n          canalInput.value = canal;\n          paginaOrigemInput.value = contexto || window.location.href;\n          setStatus('', false);\n          showWidget();\n          formFields.nome.focus();\n        }\n\n        function validarFormulario() {\n          if (!formFields.nome.value.trim()) {\n            setStatus('Por favor, informe seu nome.', true);\n            formFields.nome.focus();\n            return false;\n          }\n          if (!formFields.consentimento.checked) {\n            setStatus('É obrigatório aceitar a política de privacidade.', true);\n            formFields.consentimento.focus();\n            return false;\n          }\n          if (canalInput.value === 'email') {\n            var email = formFields.email.value.trim();\n            if (!email || !/^\S+@\S+\.\S+$/.test(email)) {\n              setStatus('Por favor, informe um e-mail válido.', true);\n              formFields.email.focus();\n              return false;\n            }\n          }\n          return true;\n        }\n\n        function sendLead(action) {\n          if (!validarFormulario()) {\n            return;\n          }\n\n          var payload = new FormData();\n          payload.append('nome', formFields.nome.value.trim());\n          payload.append('telefone', formFields.telefone.value.trim());\n          payload.append('email', formFields.email.value.trim());\n          payload.append('mensagem', formFields.mensagem.value.trim());\n          payload.append('canal', canalInput.value);\n          payload.append('pagina_origem', paginaOrigemInput.value);\n          payload.append('consentimento_lgpd', formFields.consentimento.checked ? 'true' : 'false');\n          payload.append('campo_extra', '');\n\n          setStatus('Enviando...', false);\n\n          fetch('salvar-lead.php', {\n            method: 'POST',\n            body: payload,\n            credentials: 'same-origin'\n          })\n          .then(function(response) { return response.json(); })\n          .then(function(data) {\n            if (data && data.sucesso) {\n              if (typeof gtag === 'function') {\n                gtag('event', 'conversion_lead', {\n                  'event_category': 'Lead',\n                  'event_label': canalInput.value === 'whatsapp' ? 'WhatsApp' : 'Email',\n                  'transport_type': 'beacon'\n                });\n              }\n              if (action === 'whatsapp') {\n                var telefone = '5511996332082';\n                var mensagem = encodeURIComponent(formFields.mensagem.value.trim() || 'Olá, gostaria de marcar uma aula experimental de violão!');\n                window.open('https://wa.me/' + telefone + '?text=' + mensagem, '_blank');\n                setStatus('Lead registrado com sucesso. Redirecionando para WhatsApp...', false);\n              } else {\n                setStatus('Lead registrado com sucesso. Entraremos em contato em breve.', false);\n              }\n              leadForm.reset();\n              canalInput.value = 'formulario';\n            } else {\n              setStatus((data && data.mensagem) ? data.mensagem : 'Erro ao enviar. Tente novamente.', true);\n            }\n          })\n          .catch(function() {\n            setStatus('Erro de rede. Verifique sua conexão e tente novamente.', true);\n          });\n        }\n\n        contatoTriggers.forEach(function(trigger) {\n          trigger.addEventListener('click', function(event) {\n            var canal = trigger.dataset.canal || 'whatsapp';\n            var contexto = trigger.dataset.context || window.location.href;\n            if (canal === 'whatsapp' || canal === 'email') {\n              event.preventDefault();\n              openWidgetFor(canal, contexto);\n            }\n          });\n        });\n\n        botaoAcoes.forEach(function(btn) {\n          btn.addEventListener('click', function() {\n            var action = btn.dataset.acao;\n            canalInput.value = action;\n            sendLead(action);\n          });\n        });\n\n        if (btnClose) {\n          btnClose.addEventListener('click', function() {\n            sessionStorage.setItem(STORAGE_KEY_CLOSED, '1');\n            hideWidget();\n          });\n        }\n\n        if (window.location) {\n          paginaOrigemInput.value = window.location.href;\n        }\n\n        showWidget();\n      })();\n    </script>'''

replace_email_buttons = re.compile(
    r'<button[^>]+class="[^"]*js-open-email-form[^"]*"[^>]*>(.*?)</button>',
    flags=re.S | re.I,
)

replace_whatsapp_buttons = re.compile(
    r'<a([^>]*class="[^"]*js-whatsapp-cta[^"]*")[^>]*>',
    flags=re.S | re.I,
)

for filename in ['index.html', 'deployed.html']:
    path = Path(filename)
    text = path.read_text(encoding='utf-8')

    # Convert email buttons into mailto links with shared trigger attrs.
    def email_repl(match):
        inner = match.group(1)
        return f'<a href="mailto:luisabranches.violao@gmail.com?subject=Marcar%20Aula%20Experimental" class="cta-button-secondary js-contact-trigger" data-canal="email" data-context="principal">{inner}</a>'

    text = replace_email_buttons.sub(email_repl, text)

    # Add shared trigger to whatsapp anchors if missing.
    def whatsapp_repl(match):
        tag = match.group(0)
        if 'js-contact-trigger' in tag:
            return tag
        return tag.replace('class="', 'class="js-contact-trigger ', 1).replace('href="https://api.whatsapp.com/send?phone=', 'href="https://api.whatsapp.com/send?phone=')

    text = replace_whatsapp_buttons.sub(whatsapp_repl, text)

    # Replace floating email button with shared trigger if present.
    text = re.sub(
        r'<button[^>]+class="[^"]*float-email[^"]*js-open-email-form[^"]*"([^>]*)>\s*<i[^>]*class="[^"]*fa-envelope[^"]*"[^>]*></i>\s*</button>',
        r'<a href="mailto:luisabranches.violao@gmail.com?subject=Marcar%20Aula%20Experimental" class="float float-email js-contact-trigger" data-canal="email" data-context="flutuante" aria-label="Marcar aula experimental por e-mail"><i class="fa fa-envelope my-float"></i></a>',
        text,
        flags=re.S | re.I,
    )

    # Remove old modal + script block and replace with widget_html.
    text = re.sub(
        r'<!-- Modal do formulário de contato por e-mail -->[\s\S]*?</script>\s*</body>\s*</html>',
        widget_html,
        text,
        flags=re.I,
    )

    path.write_text(text, encoding='utf-8')
    print(f'Patched {filename}')
