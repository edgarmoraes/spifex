// Modais
function abrirModal(openBtn, modal) {
  openBtn.addEventListener('click', () => {
    modalAberto = modal;
    modal.showModal();
    document.body.style.overflow = 'hidden';
  });
}

function fecharModal(closeBtn, modal, formSelector) {
  closeBtn.addEventListener('click', () => {
    fechar(modal, formSelector);
  });

  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      fechar(modal, formSelector);
    }
  });

  modal.addEventListener('close', () => {
    fechar(modal, formSelector);
  });
}

function fechar(modal, formSelector) {
  modal.close();
  document.body.style.overflow = '';
  limparCamposModal()
  document.querySelector(formSelector).reset();
}

// Elementos do DOM
const openModalBancos = document.querySelector('.adicionar-bancos');

const closeModalBancos = document.querySelector('.modal-fechar-bancos');

const modalBancos = document.querySelector('.modal-bancos');

function limparCamposModal() {
  const inputs = document.querySelectorAll(`.modal-bancos input`);
  inputs.forEach(input => {
      if (input.type !== 'submit' && input.name !== 'csrfmiddlewaretoken') {
          input.value = '';
      }
  });
}

// Event Listeners
abrirModal(openModalBancos, modalBancos, ".modal-form-bancos");
fecharModal(closeModalBancos, modalBancos, ".modal-form-bancos");

// Função para formatar o valor de um campo como moeda brasileira
function formatarCampoValorBancos(input) {
  // Remover caracteres não numéricos
  let valor = input.value.replace(/\D/g, '');

  // Remover zeros à esquerda
  valor = valor.replace(/^0+/, '');

  // Adicionar o ponto decimal nas duas últimas casas decimais
  if (valor.length > 2) {
      valor = valor.slice(0, -2) + '.' + valor.slice(-2);
  } else if (valor.length === 2) {
      valor = '0.' + valor;
  } else if (valor.length === 1) {
      valor = '0.0' + valor;
  } else {
      valor = '0.00';
  }

  // Atualizar o valor do campo
  input.value = valor;
}


document.addEventListener('DOMContentLoaded', function () {
  var linhasBancos = document.querySelectorAll('.row-bancos');

  linhasBancos.forEach(function (linha) {
      linha.addEventListener('dblclick', function () {
          // Abra o modal aqui
          const modalBancos = document.querySelector('.modal-bancos');
          modalBancos.showModal();

          // Preencha os campos do modal com os dados da linha clicada
          const banco = linha.querySelector('.banco-row').textContent;
          const agencia = linha.querySelector('.ag-row').textContent;
          const conta = linha.querySelector('.conta-row').textContent;
          const saldoInicial = linha.getAttribute('data-saldo-inicial').replace(',', '.');
          const idBanco = linha.getAttribute('data-id-banco');
          const statusBanco = linha.querySelector('.status-row').textContent.trim(); // Use trim() para remover espaços em branco

          document.getElementById('descricao-bancos').value = banco;
          document.getElementById('agencia-banco').value = agencia;
          document.getElementById('conta-banco').value = conta;
          document.getElementById('saldo-inicial').value = saldoInicial;
          document.querySelector('[name="id_banco"]').value = idBanco;
          // Corrige a seleção de elemento para o select de status e ajusta o valor baseado no texto
          const selectStatusBanco = document.querySelector('#status-banco'); // Corrige a seleção para o ID correto
          selectStatusBanco.value = statusBanco.toLowerCase() === 'ativo' ? 'ativo' : 'inativo'; // Ajusta o valor do select
      });
  });

  // Fechar o modal ao clicar no botão "Cancelar"
  var btnFechar = document.querySelector('.modal-fechar-bancos');
  btnFechar.addEventListener('click', function () {
      var modalBancos = document.querySelector('.modal-bancos');
      modalBancos.close();
  });
});

document.querySelector('.modal-form-bancos').addEventListener('submit', function(e) {
  e.preventDefault();  // Impede o envio tradicional do formulário

  // Dados do formulário
  var formData = new FormData(this);

  // Requisição AJAX
  fetch('/configuracoes/salvar_banco/', {
      method: 'POST',
      body: formData
  })
  .then(response => response.json())
  .then(data => {
      if(data.success) {
          // Feche o modal aqui
          document.querySelector('.modal-bancos').close();
          window.location.reload();
          // Atualize a lista de bancos aqui
          // Você pode adicionar o código para atualizar a lista dinamicamente sem recarregar a página
      } else {
          alert("Houve um erro ao salvar as informações.");
      }
  })
  .catch(error => console.error('Error:', error));
});