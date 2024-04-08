// Função auxiliar para resetar campos específicos de cada modal
function resetModalFields(formSelector) {
  const form = document.querySelector(formSelector);
  form?.reset();
  
  // Reset específico para o modal de bancos
  document.querySelectorAll(".modal-apagar-bancos").forEach(botao => botao.style.display = 'none');
  
  const inputs = document.querySelectorAll(`${formSelector} input`);
  inputs.forEach(input => {
    if (input.type !== 'submit' && input.name !== 'csrfmiddlewaretoken') {
      input.value = '';
    }
  });
}

// Função unificada para manipular a abertura e fechamento de modais
function handleModal(openBtnSelector, modalSelector, formSelector, config = {}) {
  const openBtn = document.querySelector(openBtnSelector);
  const modal = document.querySelector(modalSelector);

  openBtn.addEventListener('click', () => {
    modal.showModal();
    document.body.style.overflow = 'hidden';
  });

  const closeModalFunc = () => {
    modal.close();
    document.body.style.overflow = '';
    resetModalFields(formSelector);
    document.getElementById('saldo-inicial').value = "R$ "
  };

  const closeBtn = document.querySelector(config.closeBtnSelector);
  closeBtn?.addEventListener('click', closeModalFunc);
  modal.addEventListener('keydown', (e) => e.key === 'Escape' && closeModalFunc());
  modal.addEventListener('close', closeModalFunc);
}

document.addEventListener('DOMContentLoaded', () => {
  // Configuração do modal de bancos
  const modalConfig = {
    openBtn: '.adicionar-bancos', 
    modal: '.modal-bancos', 
    form: '.modal-form-bancos', 
    config: {closeBtnSelector: '.modal-fechar-bancos'}
  };

  // Aplicar configuração para o modal de bancos
  handleModal(modalConfig.openBtn, modalConfig.modal, modalConfig.form, modalConfig.config);
});


// Função para formatar o valor de um campo como moeda brasileira
function formatarCampoValor(input) {
  let valorNumerico = input.value.replace(/\D/g, '');
  let valorFloat = parseFloat(valorNumerico) / 100;
  let valorFormatado = valorFloat.toFixed(2)
    .replace('.', ',')
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  input.value = valorNumerico ? `R$ ${valorFormatado}` : 'R$ 0,00';
  if (input.value === 'R$ 0,00') {
    input.value = 'R$ 0,00';
  }
}

// Edição de banco
document.addEventListener('DOMContentLoaded', function () {
  var linhasBancos = document.querySelectorAll('.row-bancos');

  linhasBancos.forEach(function (linha) {
      linha.addEventListener('dblclick', function () {
          // Abra o modal aqui
          const modalBancos = document.querySelector('.modal-bancos');
          modalBancos.showModal();
          
          // Torna o botão de apagar visível
          document.querySelectorAll(".modal-apagar-bancos").forEach(botao => botao.style.display = 'block');

          // Preencha os campos do modal com os dados da linha clicada
          const banco = linha.querySelector('.banco-row').textContent;
          const bank_branch = linha.querySelector('.ag-row').textContent;
          const conta = linha.querySelector('.conta-row').textContent;
          const saldoInicial = linha.querySelector('.saldo-banco-row').textContent;
          const idBanco = linha.getAttribute('data-id-banco');
          const statusBanco = linha.querySelector('.status-row').textContent.trim(); // Use trim() para remover espaços em branco

          document.getElementById('bank-name').value = banco;
          document.getElementById('bank-branch').value = bank_branch;
          document.getElementById('bank-account').value = conta;
          document.getElementById('saldo-inicial').value = "R$ " + saldoInicial;
          document.querySelector('[name="bank_id"]').value = idBanco;
          const selectStatusBanco = document.getElementById('bank-status');
          selectStatusBanco.value = statusBanco.toLowerCase() === 'ativo' ? 'ativo' : 'inativo';
      });
  });

  // Fechar o modal ao clicar no botão "Cancelar"
  var btnFechar = document.querySelector('.modal-fechar-bancos');
  btnFechar.addEventListener('click', function () {
      var modalBancos = document.querySelector('.modal-bancos');
      modalBancos.close();
      
      // Torna o botão de apagar invisível
      document.querySelectorAll(".modal-apagar-bancos").forEach(botao => botao.style.display = 'none');
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Assume que o token CSRF está disponível

  // Configuração para adicionar ou atualizar um banco
  const formBancos = document.querySelector('.modal-form-bancos');
  formBancos.addEventListener('submit', function(e) {
      e.preventDefault();

      const formData = new FormData(this);
      formData.append('csrfmiddlewaretoken', csrftoken); // Adiciona o CSRF token ao formData

      fetch('/configuracoes/salvar_banco/', { // Ajuste o caminho conforme necessário
          method: 'POST',
          body: formData,
          headers: { "X-CSRFToken": csrftoken },
      })
      .then(response => response.json())
      .then(data => {
          alert(data.success ? 'Operação realizada com sucesso.' : 'Erro ao realizar operação.');
          if(data.success) {
              window.location.reload(); // Recarrega a página para mostrar as atualizações
          }
      })
      .catch(error => console.error('Erro:', error));
  });

  // Configuração para apagar um banco
  document.querySelectorAll('.modal-apagar-bancos').forEach(button => {
      button.addEventListener('click', function() {
          const idBanco = document.querySelector('input[name="bank_id"]').value;

          fetch(`/configuracoes/verificar_e_excluir_banco/${idBanco}/`, {
              method: 'POST',
              headers: {
                  "X-CSRFToken": csrftoken,
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ "csrfmiddlewaretoken": csrftoken }) // O corpo da requisição precisa ser um JSON válido
          })
          .then(response => response.json())
          .then(data => {
              alert(data.success ? 'Banco excluído com sucesso.' : 'Erro ao excluir banco.');
              if(data.success) {
                  window.location.reload(); // Recarrega a página para remover o banco excluído da listagem
              }
          })
          .catch(error => console.error('Erro:', error));
      });
  });
});