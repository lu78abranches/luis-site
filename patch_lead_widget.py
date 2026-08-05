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
    </div>

    <script>
      (function() {
        var STORAGE_KEY_CLOSED = 'luis_lead_widget_closed';
        var leadWidget = document.getElementById('lead-widget');
        var leadForm = document.getElementById('lead-widget-form');
        var btnClose = document.getElementById('lead-widget-close');
        var status = document.getElementById('lead-widget-status');
        var canalInput = document.getElementById('lead-widget-canal');
        var paginaOrigemInput = document.getElementById('lead-widget-pagina_origem');
        var botaoAcoes = document.querySelectorAll('.lead-widget-action');
        var contatoTriggers = document.querySelectorAll('.js-contact-trigger');
        var formFields = {
          nome: document.getElementById('lead-nome'),
          telefone: document.getElementById('lead-telefone'),
          email: document.getElementById('lead-email'),
          mensagem: document.getElementById('lead-mensagem'),
          consentimento: document.getElementById('lead-consentimento')
        };

        function setStatus(text, isError) {
          status.textContent = text;
          status.style.color = isError ? '#c72' : '#1a5';
        }

        function hideWidget() {
          if (!leadWidget) return;
          leadWidget.classList.add('lead-widget-hidden');
          leadWidget.setAttribute('aria-hidden', 'true');
        }

        function showWidget() {
          if (!leadWidget) return;
          if (sessionStorage.getItem(STORAGE_KEY_CLOSED) === '1') {
            hideWidget();
            return;
          }
          leadWidget.classList.remove('lead-widget-hidden');
          leadWidget.setAttribute('aria-hidden', 'false');
        }

        function openWidgetFor(canal, contexto) {
          if (!canalInput) return;
          canalInput.value = canal;
          paginaOrigemInput.value = contexto || window.location.href;
          setStatus('', false);
          showWidget();
          formFields.nome.focus();
        }

        function validarFormulario() {
          if (!formFields.nome.value.trim()) {
            setStatus('Por favor, informe seu nome.', true);
            formFields.nome.focus();
            return false;
          }
          if (!formFields.consentimento.checked) {
            setStatus('É obrigatório aceitar a política de privacidade.', true);
            formFields.consentimento.focus();
            return false;
          }
          if (canalInput.value === 'email') {
            var email = formFields.email.value.trim();
            if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
              setStatus('Por favor, informe um e-mail válido.', true);
              formFields.email.focus();
              return false;
            }
          }
          return true;
        }

        function sendLead(action) {
          if (!validarFormulario()) {
            return;
          }

          var payload = new FormData();
          payload.append('nome', formFields.nome.value.trim());
          payload.append('telefone', formFields.telefone.value.trim());
          payload.append('email', formFields.email.value.trim());
          payload.append('mensagem', formFields.mensagem.value.trim());
          payload.append('canal', canalInput.value);
          payload.append('pagina_origem', paginaOrigemInput.value);
          payload.append('consentimento_lgpd', formFields.consentimento.checked ? 'true' : 'false');
          payload.append('campo_extra', '');

          setStatus('Enviando...', false);

          fetch('salvar-lead.php', {
            method: 'POST',
            body: payload,
            credentials: 'same-origin'
          })
          .then(function(response) {
            return response.json();
          })
          .then(function(data) {
            if (data && data.sucesso) {
              if (typeof gtag === 'function') {
                gtag('event', 'conversion_lead', {
                  'event_category': 'Lead',
                  'event_label': canalInput.value === 'whatsapp' ? 'WhatsApp' : 'Email',
                  'transport_type': 'beacon'
                });
              }
              if (action === 'whatsapp') {
                var telefone = '5511996332082';
                var mensagem = encodeURIComponent(formFields.mensagem.value.trim() || 'Olá, gostaria de marcar uma aula experimental de violão!');
                window.open('https://wa.me/' + telefone + '?text=' + mensagem, '_blank');
                setStatus('Lead registrado com sucesso. Redirecionando para WhatsApp...', false);
              } else {
                setStatus('Lead registrado com sucesso. Entraremos em contato em breve.', false);
              }
              leadForm.reset();
              canalInput.value = 'formulario';
            } else {
              setStatus((data && data.mensagem) ? data.mensagem : 'Erro ao enviar. Tente novamente.', true);
            }
          })
          .catch(function() {
            setStatus('Erro de rede. Verifique sua conexão e tente novamente.', true);
          });
        }

        contatoTriggers.forEach(function(trigger) {
          trigger.addEventListener('click', function(event) {
            var canal = trigger.dataset.canal || 'whatsapp';
            var contexto = trigger.dataset.context || window.location.href;
            if (canal === 'whatsapp' || canal === 'email') {
              event.preventDefault();
              openWidgetFor(canal, contexto);
            }
          });
        });

        botaoAcoes.forEach(function(btn) {
          btn.addEventListener('click', function() {
            var action = btn.dataset.acao;
            canalInput.value = action;
            sendLead(action);
          });
        });

        if (btnClose) {
          btnClose.addEventListener('click', function() {
            sessionStorage.setItem(STORAGE_KEY_CLOSED, '1');
            hideWidget();
          });
        }

        if (window.location) {
          paginaOrigemInput.value = window.location.href;
        }

        showWidget();
      })();
    </script>
</body>
</html>'''

for filename in ['index.html', 'deployed.html']:
    path = Path(filename)
    text = path.read_text(encoding='utf-8')
    text = text.replace('class="cta-button js-whatsapp-cta"', 'class="cta-button js-contact-trigger js-whatsapp-cta" data-canal="whatsapp"')
    text = re.sub(r'<button type="button" class="cta-button-secondary js-open-email-form" data-context="([^"]+)">(.*?)</button>', r'<a href="mailto:luisabranches.violao@gmail.com?subject=Marcar%20Aula%20Experimental" class="cta-button-secondary js-contact-trigger" data-canal="email" data-context="\1">\2</a>', text, flags=re.S)
    text = re.sub(r'<button type="button" class="float float-email js-open-email-form" data-context="([^"]+)" aria-label="([^"]+)">\s*<i class="fa fa-envelope my-float"></i>\s*</button>', r'<a href="mailto:luisabranches.violao@gmail.com?subject=Marcar%20Aula%20Experimental" class="float float-email js-contact-trigger" data-canal="email" data-context="\1" aria-label="\2"><i class="fa fa-envelope my-float"></i></a>', text, flags=re.S)
    match = re.search(r'<!-- Modal do formulário de contato por e-mail -->.*?</script>\s*</body>\s*</html>', text, flags=re.S)
    if match:
        text = text[:match.start()] + widget_html
    else:
        raise RuntimeError(f'Old modal block not found in {filename}')
    path.write_text(text, encoding='utf-8')
    print(f'Patched {filename}')
