// Aparecer barra de botões
document.addEventListener('DOMContentLoaded', function () {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const botoesAcoes = document.querySelector('.botoes-acoes');
    const tabelaLancamentos = document.querySelector('.conteudo-tabela-lancamentos');
    const cancelarButton = document.querySelector('.cancelar-button');
    
    checkboxes.forEach(function (checkbox) {
      checkbox.addEventListener('change', function () {
            const algumaCheckboxMarcada = Array.from(checkboxes).some(checkbox => checkbox.checked);

            if (algumaCheckboxMarcada) {
                // Pelo menos uma checkbox marcada, exibir os botões e adicionar a margem
                botoesAcoes.style.display = 'flex';
                botoesAcoes.classList.add('mostrar');
                tabelaLancamentos.style.marginBottom = '6.5rem';
              } else {
                // Nenhuma checkbox marcada, ocultar os botões e remover a margem
                botoesAcoes.classList.remove('mostrar');
                tabelaLancamentos.style.marginBottom = '0';
              }
            });
          });
          
          cancelarButton.addEventListener('click', function () {
            checkboxes.forEach(function (checkbox) {
            checkbox.checked = false;
          });
          
          // Ocultar os botões e remover a margem
          botoesAcoes.classList.remove('mostrar');
          tabelaLancamentos.style.marginBottom = '0';
        });
      });
      
      function liquidar() {
        alert('Ação de liquidar');
      }
      
      function apagar() {
        alert('Ação de apagar');
      }
      
      
// Modais
function abrirModal(openBtn, modal, formSelector, tagInputId, tagsHiddenInputId, tagContainerId) {
  openBtn.addEventListener('click', () => {
    modalAberto = modal;
    modal.showModal();
    document.body.style.overflow = 'hidden';
  });
}

function fecharModal(closeBtn, modal, formSelector, tagInputId, tagsHiddenInputId, tagContainerId, parcelasId) {
  closeBtn.addEventListener('click', () => {
    fechar(modal, formSelector, tagInputId, tagsHiddenInputId, tagContainerId, parcelasId);
  });
  
  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      fechar(modal, formSelector, tagInputId, tagsHiddenInputId, tagContainerId, parcelasId);
    }
  });

  modal.addEventListener('close', () => {
    fechar(modal, formSelector, tagInputId, tagsHiddenInputId, tagContainerId, parcelasId);
  });
}

function fechar(modal, formSelector, tagInputId, tagsHiddenInputId, tagContainerId, parcelasId) {
  modal.close();
  document.body.style.overflow = '';
  document.querySelector(formSelector).reset();
  
  const tagContainer = document.getElementById(tagContainerId);
  while (tagContainer.firstChild) {
      tagContainer.removeChild(tagContainer.firstChild);
  }
  
  const tagInput = document.getElementById(tagInputId);
  const tagsHiddenInput = document.getElementById(tagsHiddenInputId);
  
  tagInput.value = '';
  tagsHiddenInput.value = '';

  // Adicionar o código para redefinir e ocultar o campo de parcelas
  const parcelasInput = document.getElementById(parcelasId);
  parcelasInput.value = ''; // Define o valor padrão para 1
  parcelasInput.style.display = 'none'; // Oculta o campo de parcelas
}

// Elementos do DOM
const openModalRecebimentos = document.querySelector('.recebimentos');
const openModalPagamentos = document.querySelector('.pagamentos');
const openModalTransferencias = document.querySelector('.transferencias');

const closeModalRecebimentos = document.querySelector('.modal-fechar-recebimentos');
const closeModalPagamentos = document.querySelector('.modal-fechar-pagamentos');
const closeModalTransferencias = document.querySelector('.modal-fechar-transferencias');

const modalRecebimentos = document.querySelector('.modal-recebimentos');
const modalPagamentos = document.querySelector('.modal-pagamentos');
const modalTransferencias = document.querySelector('.modal-transferencias');

// Event Listeners
abrirModal(openModalRecebimentos, modalRecebimentos, ".modal-form-recebimentos", 'tagInput-recebimentos', 'tagsHiddenInput-recebimentos', 'tag-container-recebimentos');
fecharModal(closeModalRecebimentos, modalRecebimentos, ".modal-form-recebimentos", 'tagInput-recebimentos', 'tagsHiddenInput-recebimentos', 'tag-container-recebimentos', "parcelas-section-recebimentos");

abrirModal(openModalPagamentos, modalPagamentos, ".modal-form-pagamentos", 'tagInput-pagamentos', 'tagsHiddenInput-pagamentos', 'tag-container-pagamentos');
fecharModal(closeModalPagamentos, modalPagamentos, ".modal-form-pagamentos", 'tagInput-pagamentos', 'tagsHiddenInput-pagamentos', 'tag-container-pagamentos', "parcelas-section-pagamentos");

abrirModal(openModalTransferencias, modalTransferencias, ".modal-form-transferencias");
fecharModal(closeModalTransferencias, modalTransferencias, ".modal-form-transferencias");

// Função para mostrar campo de recorrência
function mostrarOcultarParcelas(recorrenciaId, parcelasSectionId, parcelasId) {
  var recorrenciaSelect = document.getElementById(recorrenciaId);
  var parcelasSection = document.getElementById(parcelasSectionId);
  var parcelasInput = document.getElementById(parcelasId);

  console.log("recorrenciaSelect.value:", recorrenciaSelect.value);
  console.log("parcelasSection.style.display:", parcelasSection.style.display);
  console.log("parcelasInput.value:", parcelasInput.value);

  if (recorrenciaSelect.value === "sim") {
    parcelasSection.style.display = "block";
    parcelasInput.value = "";
  } else {
    parcelasSection.style.display = "none";
    parcelasInput.value = "1";
  }
}

function mostrarParcelasRecebimentos() {
  mostrarOcultarParcelas("recorrencia-recebimentos", "parcelas-section-recebimentos", "parcelas-recebimentos");
}

function mostrarParcelasPagamentos() {
  mostrarOcultarParcelas("recorrencia-pagamentos", "parcelas-section-pagamentos", "parcelas-pagamentos");
}
  
// Função para formatar o valor de um campo como moeda brasileira
function formatarCampoValor(input) {
  // Obtém apenas os dígitos do valor atual
  var valorNumerico = input.value.replace(/\D/g, '');

  // Converte o valor para número
  var valorDecimal = parseFloat(valorNumerico) / 100;

  // Formata o valor como moeda brasileira
  var valorFormatado = valorDecimal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

  // Adiciona o "R$" ao valor formatado e atualiza o campo
  input.value = "R$ " + (isNaN(valorDecimal) ? "0,00" : valorFormatado.replace('R$', '').trim());

  // Atualizar o valor do campo number
  document.getElementById('valor_number').value = valorNumerico / 100;

}


// Adiciona um evento de teclado para detectar 'Shift + D'
document.addEventListener('keydown', function(event) {
    if (event.shiftKey && event.key === 'D') {
        event.preventDefault(); // Evita a inserção da tecla no campo
        preencherDataEFocus();
    }
});

// Função para preencher os campos de data e mover o foco para o campo de descrição
function preencherDataEFocus() {
    var dataRecebimentos = document.getElementById("data-recebimentos");
    var dataPagamentos = document.getElementById("data-pagamentos");
    var dataTransferencias = document.getElementById("data-transferencias");

    // Obter a data atual
    var dataAtual = new Date();
    var dia = ('0' + dataAtual.getDate()).slice(-2);
    var mes = ('0' + (dataAtual.getMonth() + 1)).slice(-2);
    var ano = dataAtual.getFullYear();

    // Formatando como "yyyy-mm-dd" para ser aceito pelo campo de data
    var dataFormatada = ano + '-' + mes + '-' + dia;

    // Preenche os campos de data apenas no modal que está aberto
    if (modalAberto === modalRecebimentos) {
        dataRecebimentos.value = dataFormatada;
        document.getElementById('descricao-recebimentos').focus();
    } else if (modalAberto === modalPagamentos) {
        dataPagamentos.value = dataFormatada;
        document.getElementById('descricao-pagamentos').focus();
    } else if (modalAberto === modalTransferencias) {
        dataTransferencias.value = dataFormatada;
        document.getElementById('valor-transferencias').focus();
    }
}


// Tags
function initializeTagInputs(inputId, containerId, hiddenInputId) {
    document.getElementById(inputId).addEventListener('keydown', function(event) {
      if (event.key === 'Enter' || event.key === ',') {
        event.preventDefault();
        addTag(this.value.trim(), containerId, hiddenInputId);
        this.value = ''; // Limpar o campo de entrada após adicionar uma tag
      }
    });
  }

  function addTag(tag, containerId, hiddenInputId) {
    if (tag !== '') {
      const tagContainer = document.getElementById(containerId);
      const tagElement = document.createElement('div');
      const tagText = document.createElement('span');
      const tagInput = document.createElement('input');

      tagElement.classList.add('tag');
      tagText.textContent = tag;
      tagElement.appendChild(tagText);

      tagInput.value = tag;
      tagInput.addEventListener('blur', function() {
        saveTagEdit(tagInput, tagText);
        updateHiddenInput(containerId, hiddenInputId);
      });

      tagInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
          event.preventDefault();
          saveTagEdit(tagInput, tagText);
          updateHiddenInput(containerId, hiddenInputId);
        }
      });
      
      tagElement.addEventListener('click', function() {
        let singleClick = true;
        
        setTimeout(function() {
            if (singleClick) {
                tagInput.style.display = 'inline';
                tagText.style.display = 'none';
                tagInput.focus();
            }
        }, 500); // Tempo de intervalo para contar o click único
    
        tagElement.addEventListener('dblclick', function() {
          const isBeingEdited = tagInput.style.display === 'inline';
      
          setTimeout(() => {
              if (!isBeingEdited) {
                  this.remove();
                  updateHiddenInput(containerId, hiddenInputId);
              }
          }, 250); // Ajuste o tempo conforme necessário
      });
    });

      tagElement.appendChild(tagInput);
      tagContainer.appendChild(tagElement);
      updateHiddenInput(containerId, hiddenInputId);
    }
  }

  function saveTagEdit(tagInput, tagText) {
    tagText.textContent = tagInput.value;
    tagInput.style.display = 'none';
    tagText.style.display = 'inline';
  }

  function updateHiddenInput(containerId, hiddenInputId) {
    const tagsHiddenInput = document.getElementById(hiddenInputId);
    const tagElements = document.querySelectorAll(`#${containerId} .tag span`);
    const tagsArray = Array.from(tagElements).map(tag => tag.textContent);
    tagsHiddenInput.value = tagsArray.join(',');
  }

  // Initialize for recebimentos
  initializeTagInputs('tagInput-recebimentos', 'tag-container-recebimentos', 'tagsHiddenInput-recebimentos');
  
  // Initialize for pagamentos
  initializeTagInputs('tagInput-pagamentos', 'tag-container-pagamentos', 'tagsHiddenInput-pagamentos');