// Apagar lançamentos da tabela
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('apagar-button').addEventListener('click', function() {
      var idsSelecionados = [];
      var checkboxesSelecionadas = document.querySelectorAll('.checkbox-personalizado:checked');
      checkboxesSelecionadas.forEach(function(checkbox) {
          idsSelecionados.push(checkbox.getAttribute('data-id'));
      });

        fetch('/fluxo_de_caixa/deletar-entradas/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({ids: idsSelecionados})
      })
      .then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              checkboxesSelecionadas.forEach(function(checkbox) {
                  var linhaParaRemover = checkbox.closest('tr');
                  linhaParaRemover.remove();
              });
          }
      })
      .catch(error => console.error('Erro:', error));
  });
});

function getCsrfToken() {
  return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

// Selecionar checkboxes com o shift clicado
let ultimoCheckboxClicado;

document.addEventListener('click', function(e) {
    if (!e.target.classList.contains('checkbox-personalizado')) return;
    let checkboxAtual = e.target;

    if (e.shiftKey && ultimoCheckboxClicado) {
        let checkboxes = Array.from(document.querySelectorAll('.checkbox-personalizado'));
        let startIndex = checkboxes.indexOf(ultimoCheckboxClicado);
        let endIndex = checkboxes.indexOf(checkboxAtual);
        let inverterSelecao = checkboxAtual.checked;

        for (let i = Math.min(startIndex, endIndex); i <= Math.max(startIndex, endIndex); i++) {
            checkboxes[i].checked = inverterSelecao;
        }
    }

    ultimoCheckboxClicado = checkboxAtual;
});

// Aparecer barra de botões
document.addEventListener('DOMContentLoaded', function () {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const botoesAcoes = document.querySelector('.botoes-acoes');
    const tabelaLancamentos = document.querySelector('.conteudo-tabela-lancamentos');
    const cancelarButton = document.querySelector('.cancelar-button');
    const apagarButton = document.querySelector('.apagar-button');
    
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

          apagarButton.addEventListener('click', function () {
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






// Lógica de Abertura Condicional dos Modais
document.querySelectorAll('.row-lancamentos').forEach(row => {
  row.addEventListener('dblclick', function() {
      const credito = row.querySelector('.credito-row').textContent.trim();
      const debito = row.querySelector('.debito-row').textContent.trim();

      if (credito && !debito) {
          abrirModalRecebimentosEdicao(this);
      } else if (!credito && debito) {
          abrirModalPagamentosEdicao(this);
      }
  });
});


document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
      if (document.getElementById('modal-recebimentos').open) {
          fecharModalRecebimentosEdicao();
      } else if (document.getElementById('modal-pagamentos').open) {
          fecharModalPagamentosEdicao();
      }
  }
});


function abrirModalRecebimentosEdicao(row) {
  // Preenchendo os campos com os dados da linha
  const vencimento = row.querySelector('.vencimento-row').textContent.trim();
  document.getElementById('data-recebimentos').value = formatarDataParaInput(vencimento);

  document.getElementById('descricao-recebimentos').value = row.querySelector('.descricao-row').textContent.trim();

  const observacao = row.querySelector('.obs-row').childNodes[0].textContent.trim();
  document.getElementById('observacao-recebimentos').value = observacao;

  const tagsTexto = row.querySelector('.d-block').textContent.trim();
  const tags = tagsTexto.replace("Tags: ", ""); // Remove o texto "Tags: "
  document.getElementById('tagInput-recebimentos').value = tags;

  // Simulando o enter
  const event = new KeyboardEvent('keydown', {'key': 'Enter'});
  document.getElementById('tagInput-recebimentos').dispatchEvent(event);

  // Código para os demais campos...

  document.getElementById('modal-recebimentos').showModal();
}


function fecharModalRecebimentosEdicao() {
  // Limpando os campos do modal
  document.querySelectorAll('.modal-form-recebimentos input').forEach(input => input.value = '');
  
  // Mostrar Recorrência
  document.querySelectorAll('.modal-recorrencia, .recorrencia-label').forEach(element => {
      element.style.display = 'block';
  });

  document.getElementById('modal-recebimentos').close();
}

function formatarDataParaInput(data) {
  const partes = data.split('/');
  return partes.reverse().join('-');
}


function abrirModalPagamentosEdicao(row) {
  // Preenchendo os campos com os dados da linha
  const vencimento = row.querySelector('.vencimento-row').textContent.trim();
  document.getElementById('data-pagamentos').value = formatarDataParaInput(vencimento);

  document.getElementById('descricao-pagamentos').value = row.querySelector('.descricao-row').textContent.trim();

  const observacao = row.querySelector('.obs-row').childNodes[0].textContent.trim();
  document.getElementById('observacao-pagamentos').value = observacao;

  const tagsTexto = row.querySelector('.d-block').textContent.trim();
  const tags = tagsTexto.replace("Tags: ", ""); // Remove o texto "Tags: "
  document.getElementById('tagInput-pagamentos').value = tags;

  // Simulando o enter
  const event = new KeyboardEvent('keydown', {'key': 'Enter'});
  document.getElementById('tagInput-pagamentos').dispatchEvent(event);

  // Código para os demais campos...

  document.getElementById('modal-pagamentos').showModal();
}

function fecharModalPagamentosEdicao() {
  // Limpando os campos do modal
  document.querySelectorAll('.modal-form-pagamentos input').forEach(input => input.value = '');
  
  document.getElementById('modal-pagamentos').close();
}

function formatarDataParaInput(data) {
  const partes = data.split('/');
  return partes.reverse().join('-');
}


















// Função para mostrar campo de recorrência
function mostrarParcelasRecebimentos() {
  var select = document.getElementById('recorrencia-recebimentos');
  var section = document.getElementById('parcelas-section-recebimentos');
  var input = document.getElementById('parcelas-recebimentos');

  if (select.value === 'sim') {
      section.style.display = 'block';
      input.value = '';  // Removido o valor '1' aqui
  } else {
      section.style.display = 'none';
      input.value = '1';
  }
}

function mostrarParcelasPagamentos() {
  var select = document.getElementById('recorrencia-pagamentos');
  var section = document.getElementById('parcelas-section-pagamentos');
  var input = document.getElementById('parcelas-pagamentos');

  if (select.value === 'sim') {
      section.style.display = 'block';
      input.value = '';  // Removido o valor '1' aqui
  } else {
      section.style.display = 'none';
      input.value = '1';
  }
}

// Função para formatar o valor de um campo como moeda brasileira
function formatarCampoValorRecebimentos(input) {
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

function formatarCampoValorPagamentos(input) {
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
