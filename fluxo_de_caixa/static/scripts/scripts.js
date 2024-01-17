// Apagar lançamentos da Tabela
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
              window.location.reload();
          }
      })
      .catch(error => console.error('Erro:', error));
  });
});

function getCsrfToken() {
  return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

// Selecionar checkboxes com o shift clicado
document.addEventListener('click', function(e) {
  if (!e.target.classList.contains('checkbox-personalizado')) return;
  let checkboxAtual = e.target;

  if (e.shiftKey && ultimoCheckboxClicado) {
      let checkboxes = Array.from(document.querySelectorAll('.checkbox-personalizado'));
      let startIndex = checkboxes.indexOf(ultimoCheckboxClicado);
      let endIndex = checkboxes.indexOf(checkboxAtual);
      let inverterSelecao = checkboxAtual.checked;

      for (let i = Math.min(startIndex, endIndex); i <= Math.max(startIndex, endIndex); i++) {
          // Verificar se a linha da tabela onde o checkbox está localizado é visível
          let tr = checkboxes[i].closest('tr');
          if (tr && tr.style.display !== 'none') {
              checkboxes[i].checked = inverterSelecao;
          }
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
    document.body.style.marginRight = '17px';
    document.querySelector('.nav-bar').style.marginRight = '17px';
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
  modalAberto = null;
  document.body.style.overflow = '';
  document.body.style.marginRight = '';
  document.querySelector('.nav-bar').style.marginRight = '';
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


// Evento para editar lançamentos ao clicar duas vezes nas células da tabela
document.querySelectorAll('.row-lancamentos td:not(.checkbox-row)').forEach(cell => {
  cell.addEventListener('dblclick', function() {
      handleCellDoubleClick(cell);
  });
});

// Fecha os modais ao pressionar a tecla Escape
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') {
      fecharModais();
  }
});

function handleCellDoubleClick(cell) {
  const row = cell.closest('.row-lancamentos');
  abrirModalEdicao(row);
}

function abrirModalEdicao(row) {
  const credito = row.querySelector('.credito-row').textContent.trim();
  const debito = row.querySelector('.debito-row').textContent.trim();

  if (credito && !debito) {
      abrirModalRecebimentosEdicao(row);
  } else if (!credito && debito) {
      abrirModalPagamentosEdicao(row);
  }
}

function fecharModais() {
  if (document.getElementById('modal-recebimentos').open) {
      fecharModalRecebimentosEdicao();
  } else if (document.getElementById('modal-pagamentos').open) {
      fecharModalPagamentosEdicao();
  }
}

function abrirModalRecebimentosEdicao(row) {
  // Preenchendo os campos com os dados da linha para o modal de recebimentos
  preencherDadosModal(row, 'recebimentos');
  document.getElementById('modal-recebimentos').showModal();
}

function abrirModalPagamentosEdicao(row) {
  // Preenchendo os campos com os dados da linha para o modal de pagamentos
  preencherDadosModal(row, 'pagamentos');
  document.getElementById('modal-pagamentos').showModal();
}

function preencherDadosModal(row, tipo) {
  const vencimento = row.querySelector('.vencimento-row').textContent.trim();
  document.getElementById(`data-${tipo}`).value = formatarDataParaInput(vencimento);

  const valor = row.querySelector(`.${tipo === 'recebimentos' ? 'credito' : 'debito'}-row`).textContent.trim();
  document.getElementById(`valor-${tipo}`).value = valor.replace(',', '.');

  document.getElementById(`descricao-${tipo}`).value = row.querySelector('.descricao-row').textContent.trim();
  document.getElementById(`observacao-${tipo}`).value = row.querySelector('.obs-row').childNodes[0].textContent.trim();

  const tags = extrairTags(row);
  document.getElementById(`tagInput-${tipo}`).value = tags;

  document.getElementById(`conta-contabil-${tipo}`).value = row.dataset.contaContabil;

  const parcelas = row.querySelector('.parcela-row').textContent.trim();
  document.getElementById(`parcelas-${tipo}`).type = 'text';
  document.getElementById(`parcelas-${tipo}`).value = parcelas;

  const lancamentoId = row.querySelector('.checkbox-personalizado').getAttribute('data-id');
  document.querySelector(`[name="lancamento_id"]`).value = lancamentoId;

  simularEnter(`tagInput-${tipo}`);
}

function extrairTags(row) {
  const tagsContainer = row.querySelector('.d-block');
  return tagsContainer ? tagsContainer.textContent.trim().replace(/^Tags:\s*/, '') : '';
}

function simularEnter(elementId) {
  const event = new KeyboardEvent('keydown', {'key': 'Enter'});
  document.getElementById(elementId).dispatchEvent(event);
}

function fecharModalRecebimentosEdicao() {
  limparCamposModal('recebimentos');
  document.getElementById('modal-recebimentos').close();
}

function fecharModalPagamentosEdicao() {
  limparCamposModal('pagamentos');
  document.getElementById('modal-pagamentos').close();
}

function limparCamposModal(tipo) {
  document.querySelectorAll(`.modal-form-${tipo} input`).forEach(input => input.value = '');
}

function formatarDataParaInput(data) {
  // Formata a data para o formato apropriado para input[type="date"]
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
  if (modalAberto && event.shiftKey && event.key === 'D') {
      event.preventDefault();
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


// Soma de valores no campo de liquidar
function calcularTotal() {
  let total = 0;

  // Somar os valores apenas das linhas com checkboxes selecionadas
  document.querySelectorAll('.row-lancamentos').forEach(row => {
      const checkbox = row.querySelector('.checkbox-personalizado');

      if (checkbox && checkbox.checked) {
          const credito = row.querySelector('.credito-row').textContent.trim();
          const debito = row.querySelector('.debito-row').textContent.trim();

          if (credito) {
              total += formatarValor(credito);
          }

          if (debito) {
              total -= formatarValor(debito);
          }
      }
  });

  // Atualizar o campo de total a liquidar
  const totalFormatado = total.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
  });
  document.querySelector('.total-liquidar-row label').textContent = totalFormatado;
}

function formatarValor(valorTexto) {
  // Remove pontos e substitui vírgula por ponto para conversão para número
  return parseFloat(valorTexto.replace(/\./g, '').replace(',', '.'));
}

// Adicionar evento listener para as checkboxes para recalcular o total quando uma checkbox é alterada
document.querySelectorAll('.checkbox-personalizado').forEach(checkbox => {
  checkbox.addEventListener('change', calcularTotal);
});

// Chamar a função calcularTotal inicialmente
calcularTotal();


document.getElementById('formulario-filtros').addEventListener('submit', function(e) {
  e.preventDefault();  // Previne a submissão normal do formulário

  // Captura os valores do formulário
  var formData = new FormData(this);
  var url = '{% url "filtrar_lancamentos" %}' + '?' + new URLSearchParams(formData).toString();

  fetch(url, {
      method: 'GET',
      headers: {
          'X-Requested-With': 'XMLHttpRequest',  // Importante para a view reconhecer como Ajax
      }
  })
  .then(response => response.json())
  .then(data => {
      atualizarTabela(data.dados);
  })
  .catch(error => console.error('Erro:', error));
});


// Filtros
function buscarDatasDoMes(mesSelecionado, callback) {
  if (!mesSelecionado) {
      callback(null, null);
      return;
  }

  fetch(`/meses_filtro/${mesSelecionado}`)
      .then(response => response.json())
      .then(data => {
          callback(data.inicio_mes, data.fim_mes);
      })
      .catch(error => {
          console.error('Erro ao buscar datas:', error);
          callback(null, null);
      });
}

function filtrarTabela() {
  var filtroMes = document.getElementById("meses").value;

  buscarDatasDoMes(filtroMes, function(inicioMes, fimMes) {
      var inicioMesDate = inicioMes ? new Date(inicioMes) : null;
      var fimMesDate = fimMes ? new Date(fimMes) : null;

      var filtroDescricao = document.getElementById("caixa-pesquisa").value.toUpperCase();
      var filtroTags = document.getElementById("caixa-pesquisa-tags").value.toUpperCase();
      var filtroContaContabil = document.getElementById("contas-contabeis").value.toUpperCase();

      var tabela = document.getElementById("tabela-lancamentos");
      var tr = tabela.getElementsByTagName("tr");

      for (var i = 0; i < tr.length; i++) {
          var tdDescricao = tr[i].getElementsByClassName("descricao-row")[0];
          var tdObservacao = tr[i].getElementsByClassName("obs-row")[0];
          var contaContabil = tr[i].getAttribute('data-conta-contabil').toUpperCase();
          var tdVencimento = tr[i].getElementsByClassName("vencimento-row")[0];
          var dataVencimento = new Date(tdVencimento.textContent.split('/').reverse().join('-'));

          var txtDescricao = tdDescricao ? tdDescricao.textContent || tdDescricao.innerText : "";
          var txtObservacao = tdObservacao ? tdObservacao.textContent.split("Tags:")[0].trim() : "";

          var descricaoObservacaoMatch = (txtDescricao.toUpperCase().indexOf(filtroDescricao) > -1 || txtObservacao.toUpperCase().indexOf(filtroDescricao) > -1);
          var tagMatch = filtroTags === "" || tr[i].textContent.toUpperCase().indexOf(filtroTags) > -1;
          var contaContabilMatch = filtroContaContabil === "" || contaContabil.toUpperCase().indexOf(filtroContaContabil) > -1;
          var mesMatch = (!inicioMesDate && !fimMesDate) || (dataVencimento >= inicioMesDate && dataVencimento <= fimMesDate);

          tr[i].style.display = descricaoObservacaoMatch && tagMatch && contaContabilMatch && mesMatch ? "" : "none";
      }
  });
}

// Adiciona ouvintes de evento para as caixas de pesquisa e seleção de conta contábil
document.getElementById('caixa-pesquisa').addEventListener('keyup', filtrarTabela);
document.getElementById('caixa-pesquisa-tags').addEventListener('keyup', filtrarTabela);
document.getElementById('contas-contabeis').addEventListener('change', filtrarTabela);
document.getElementById('meses').addEventListener('change', filtrarTabela);