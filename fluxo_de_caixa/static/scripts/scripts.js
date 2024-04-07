// Evitar bancos iguais e datas futuras no processo de transferência
document.addEventListener("DOMContentLoaded", function() {
  const formularioTransferencia = document.querySelector(".modal-form-transferencias");

  formularioTransferencia.addEventListener("submit", function(e) {
      const bancoSaidaId = document.getElementById("banco-saida").value;
      const bancoEntradaId = document.getElementById("banco-entrada").value;
      const dataTransferencia = new Date(document.getElementById("data-transferencias").value);
      const hoje = new Date();
      hoje.setHours(0, 0, 0, 0); // Ajusta a data de hoje para meia-noite para garantir a comparação correta

      // Verifica se o banco de saída é igual ao banco de entrada
      if (bancoSaidaId === bancoEntradaId) {
          e.preventDefault(); // Impede o envio do formulário
          alert("O banco de saída não pode ser igual ao banco de entrada. Por favor, selecione bancos diferentes.");
          return; // Interrompe a execução do evento
      }

      // Verifica se a data de transferência é maior que a data atual
      if (dataTransferencia > hoje) {
          e.preventDefault(); // Impede o envio do formulário
          alert("A data da transferência não pode ser futura. Por favor, selecione a data de hoje ou uma data passada.");
      }
  });
});

// Função para formatar o amount de texto para número
function formatAmountBalance(strAmount) {
  // Remove pontos e substitui vírgula por ponto para conversão para número
  // Garante que o strAmount é uma string antes de fazer as substituições
  strAmount = strAmount.toString();
  var numericAmount = strAmount.replace(/\./g, '').replace(',', '.');
  return parseFloat(numericAmount);
}

// Função para atualizar o saldo do banco selecionado
function atualizarSaldoBanco() {
  // Inicializar o amount total a liquidar
  let totalAmountToSettle = 0;
  
  // Obter o amount total a liquidar dos lançamentos selecionados
  document.querySelectorAll('.row-lancamentos').forEach(row => {
    const checkbox = row.querySelector('.checkbox-personalizado');
    if (checkbox && checkbox.checked) {
      const credito = row.querySelector('.credito-row').textContent.trim();
      const debito = row.querySelector('.debito-row').textContent.trim();

      if (credito) {
        totalAmountToSettle += formatAmountBalance(credito);
      }
      if (debito) {
        totalAmountToSettle -= formatAmountBalance(debito);
      }
    }
  });

  // Iterar por todos os checkboxes dos bancos
  document.querySelectorAll('.checkbox-personalizado-liquidacao').forEach(checkbox => {
    if (checkbox.checked) {
      // Encontrar o elemento de saldo inicial do banco correspondente
      let saldoInicialEl = checkbox.closest('.row-bancos').querySelector('[name="saldo_inicial"]');
      let saldoInicial = formatAmountBalance(saldoInicialEl.textContent);
      
      // Calcular o novo saldo
      let novoSaldo = saldoInicial + totalAmountToSettle;

      // Atualizar o elemento do saldo no formulário
      document.querySelector('[name="saldo-liquidacao"]').textContent = novoSaldo.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      });
    }
  });
}

// Adicionar evento listener para as checkboxes dos bancos para atualizar o saldo quando uma checkbox é alterada
document.querySelectorAll('.checkbox-personalizado-liquidacao').forEach(checkbox => {
  checkbox.addEventListener('change', function() {
    atualizarSaldoBanco();
    calcularTotal(); // Recalcular o total a liquidar se necessário
  });
});

// Chamar a função atualizarSaldoBanco inicialmente para definir o saldo correto
atualizarSaldoBanco();

// Campo de liquidação parcial
document.addEventListener('DOMContentLoaded', function() {
  const containerLancamentosSelecionados = document.getElementById('lancamentos-selecionados');

  // Ouvinte de evento para capturar 'change' em checkboxes 'botao-parcial'
  // dentro do contêiner de lançamentos selecionados
  containerLancamentosSelecionados.addEventListener('change', function(event) {
    if (event.target.classList.contains('botao-parcial')) {
      // Manipula a visibilidade da seção 'amount-parcial-liquidacao' com base no estado do checkbox
      const lancamentoSelecionado = event.target.closest('.lancamentos-selecionados');
      const partialAmountSection = lancamentoSelecionado.querySelector('.amount-parcial-liquidacao');
      partialAmountSection.style.display = event.target.checked ? 'block' : 'none';
      
      atualizarEstadoColunas();
    }
  });
  
  // Função para atualizar o estado das colunas baseada nos checkboxes 'botao-parcial'
  function atualizarEstadoColunas() {
    const todosBotoesParcial = document.querySelectorAll('.botao-parcial');
    const algumAtivado = Array.from(todosBotoesParcial).some(checkbox => checkbox.checked);
    const labelParcial = document.querySelector('.label-parcial');
    
    // Seleciona todos os elementos que devem ter suas colunas ajustadas
    const elementosParaAjustar = document.querySelectorAll('.lancamentos-selecionados, .label-lancamentos-selecionados');

    // Adiciona ou remove a classe 'ativo' com base no estado dos checkboxes
    elementosParaAjustar.forEach(el => {
      if (algumAtivado) {
        el.classList.add('ativo');
        if (labelParcial) labelParcial.style.display = 'block';
      } else {
        el.classList.remove('ativo');
        if (labelParcial) labelParcial.style.display = 'none';
      }
    });
  }
});


document.addEventListener('DOMContentLoaded', function() {
  const botaoLiquidacao = document.getElementById('liquidar-button');
  const modalLiquidacao = document.getElementById('modal-liquidacoes');

  botaoLiquidacao.addEventListener('click', function() {
      modalLiquidacao.showModal(); // Abre o modal

      // Esconde todos os campos de amount parcial inicialmente
      document.querySelectorAll('.amount-parcial-liquidacao').forEach(campo => {
          campo.style.display = 'none'; // Esconde todos os campos de amount parcial inicialmente
      });

      let algumBotaoParcialAtivado = false;

      // Busca todos os checkboxes marcados na tabela de lançamentos
      const checkboxesMarcadas = document.querySelectorAll('.tabela-lancamentos .checkbox-personalizado:checked');

      checkboxesMarcadas.forEach(checkbox => {
          const uuid = checkbox.getAttribute('data-uuid-row'); // Pega o UUID do lançamento
          const id = checkbox.getAttribute('data-id'); // Pega o ID do lançamento

          if (uuid !== "None") {
              const botaoParcial = document.querySelector(`#botao-parcial-${id}`);
              if (botaoParcial) {
                  botaoParcial.checked = true; // Ativa o checkbox
                  algumBotaoParcialAtivado = true; // Indica que pelo menos um botão parcial foi ativado

                  // Adiciona classe 'travado' para prevenir desmarcação
                  botaoParcial.classList.add('travado');

                  // Encontra o campo de amount parcial específico para este lançamento e o torna visível
                  const partialAmountSection = document.querySelector(`#amount-parcial-liquidacao-${id}`);
                  if (partialAmountSection) {
                      partialAmountSection.style.display = 'block'; // Mostra o campo de amount parcial específico
                  }
              }
          }
      });

      // Prevenir desmarcação dos botões parciais 'travados'
      document.querySelectorAll('.botao-parcial.travado').forEach(botao => {
          botao.addEventListener('click', function(event) {
              event.preventDefault();
          });
      });

      // Garante que a seção de amount parcial seja visível para botões parciais ativos
      document.querySelectorAll('.botao-parcial').forEach(botao => {
          const lancamentoSelecionado = botao.closest('.lancamentos-selecionados');
          if (botao.checked) {
              const partialAmountSection = lancamentoSelecionado.querySelector('.amount-parcial-liquidacao');
              if (partialAmountSection) {
                  partialAmountSection.style.display = 'block';
              }
          }
      });

      // Atualiza as classes 'ativo' conforme necessário
      atualizarClassesAtivo(algumBotaoParcialAtivado);
  });

  // Função para atualizar as classes 'ativo'
  function atualizarClassesAtivo(ativado) {
      const labelLancamentosSelecionados = document.querySelectorAll('.lancamentos-selecionados, .label-lancamentos-selecionados');
      const labelParcial = document.querySelector('.label-parcial');
      labelLancamentosSelecionados.forEach(el => {
          el.classList.toggle('ativo', ativado);
          labelParcial.style.display = ativado ? 'block' : 'none';
      });
  }

  // Opcional: Adiciona um ouvinte de eventos para fechar o modal no botão de cancelar, se houver
  const botaoFechar = modalLiquidacao.querySelector('.modal-fechar-liquidacoes');
  if (botaoFechar) {
      botaoFechar.addEventListener('click', function() {
          modalLiquidacao.close(); // Fecha o modal
      });
  }
});

// Passa informações do fluxo para o modal de liquidação
document.addEventListener('DOMContentLoaded', function() {
  inicializarAtualizacaoDeLancamentos();
});

function inicializarAtualizacaoDeLancamentos() {
  document.querySelectorAll('.tabela-lancamentos .checkbox-personalizado')
      .forEach(checkbox => checkbox.addEventListener('change', atualizarLancamentosSelecionados));
}

function atualizarLancamentosSelecionados() {
  const container = document.getElementById('lancamentos-selecionados');
  limparContainer(container);
  const checkboxesMarcadas = buscarCheckboxesMarcadas();
  checkboxesMarcadas.forEach(criarLancamentoSelecionadoElemento);
}

function buscarCheckboxesMarcadas() {
  return document.querySelectorAll('.tabela-lancamentos .checkbox-personalizado:checked');
}

function limparContainer(container) {
  container.innerHTML = '';
}

function criarLancamentoSelecionadoElemento(checkbox) {
  const lancamentoDados = extrairDadosLancamento(checkbox);
  const div = montarDivLancamento(lancamentoDados);
  document.getElementById('lancamentos-selecionados').appendChild(div);
  configureInitialValueState(div, lancamentoDados.id);
}

function extrairDadosLancamento(checkbox) {
  const row = checkbox.closest('.row-lancamentos');
  const id = checkbox.getAttribute('data-id');
  return {
      id: id,
      description: row.querySelector('.description-row').textContent,
      due_date: row.querySelector('.due_date-row').textContent,
      observation: extractObservation(row),
      amount: extractAmount(row),
      transaction_type: extractTransactionType(row)
  };
}

function extractObservation(row) {
  let observation = row.querySelector('.observation-row').textContent.trim();
  return observation.split('Tags:')[0].trim();
}

function extractAmount(row) {
  const debitAmount = row.querySelector('.debito-row').textContent;
  const creditAmount = row.querySelector('.credito-row').textContent;
  return debitAmount || creditAmount;
}

function extractTransactionType(row) {
  return row.querySelector('.debito-row').textContent ? "Débito" : "Crédito";
}

function montarDivLancamento({id, description, due_date, observation, amount, transaction_type}) {
  const div = document.createElement('div');
  div.classList.add('lancamentos-selecionados');
  div.innerHTML = `
    <section class="modal-flex data-liquidacao">
        <input class="modal-data data-liquidacao" id="data-liquidacao-${id}" type="date" name="data-liquidacao-${id}" value="${formatarDataParaInput(due_date)}" required>
    </section>
    <section class="modal-flex">
        <input class="modal-description" id="description-liquidacao-${id}" maxlength="100" type="text" name="description-liquidacao-${id}" value="${description}" readonly style="background-color: #B5B5B5; color: #FFFFFF;">
    </section>
    <section class="modal-flex">
        <input class="modal-obs" id="observation-liquidacao-${id}" maxlength="100" type="text" name="observation-liquidacao-${id}" value="${observation}">
    </section>
    <section class="modal-flex">
        <input class="modal-amount amount-liquidacao-total" id="amount-liquidacao-${id}" type="text" name="amount-liquidacao-${id}" oninput="formatAmount(this)" value="R$ ${amount}" readonly required style="background-color: #B5B5B5; color: #FFFFFF;">
    </section>
    <section class="modal-flex transaction_type-liquidacao">
        <input class="modal-transaction_type" id="transaction_type-liquidacao-${id}" type="text" name="transaction_type-liquidacao-${id}" value="${transaction_type}" readonly style="background-color: #B5B5B5; color: #FFFFFF;">
    </section>
    <section class="modal-botao-parcial">
      <div>
      <label class="form-switch"><input id="botao-parcial-${id}" class="botao-parcial" type="checkbox"><i></i></label>
      </div>
    </section>
    <section class="modal-flex amount-parcial-liquidacao" style="display:none;">
      <input class="modal-amount amount-parcial" id="amount-parcial-liquidacao-${id}" type="text" name="amount-parcial-liquidacao-${id}" oninput="formatAmount(this)" value="R$ " required>
    </section>
    `;
  ajustarDataDeLiquidacaoSeNecessario(div, id, due_date);
  return div;
}
  
function configureInitialValueState(div, id) {
    const botaoParcial = div.querySelector('.botao-parcial');
    botaoParcial.addEventListener('change', function() {
        const partialAmountField = div.querySelector('.amount-parcial-liquidacao');
        partialAmountField.style.display = botaoParcial.checked ? 'block' : 'none';
    });
}

function ajustarDataDeLiquidacaoSeNecessario(div, id, originalDueDate) {
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0); // Zera o horário para comparar apenas as datas
  const dueDate = converterDataStringParaDate(formatarDataParaInput(originalDueDate));

  if (dueDate > hoje) {
    const campoDataLiquidacao = div.querySelector(`#data-liquidacao-${id}`);
    campoDataLiquidacao.value = formatarDataAtualParaInput();
  }
}

function formatarDataAtualParaInput() {
  const dataAtual = new Date();
  const ano = dataAtual.getFullYear();
  const mes = String(dataAtual.getMonth() + 1).padStart(2, '0'); // getMonth() retorna mês de 0 a 11
  const dia = String(dataAtual.getDate()).padStart(2, '0');
  return `${ano}-${mes}-${dia}`;
}

function converterDataStringParaDate(dataString) {
  const partes = dataString.split('-');
  return new Date(partes[0], partes[1] - 1, partes[2]);
}


// Botão de Liquidar
document.getElementById('salvar-liquidacao').addEventListener('click', async function(event) {
  event.preventDefault();
  
  const liquidacaoSelecionada = document.querySelector('.checkbox-personalizado-liquidacao:checked');
  if (!liquidacaoSelecionada) {
    alert('Por favor, selecione um banco para a liquidação antes de prosseguir.');
    return;
  }

  const nomeBancoSelecionado = liquidacaoSelecionada.closest('.row-bancos').querySelector('.banco-liquidacao').getAttribute('data-nome-banco');
  const idBancoSelecionado = liquidacaoSelecionada.closest('.row-bancos').querySelector('.banco-liquidacao').getAttribute('data-id-banco');
  let selectedRows = document.querySelectorAll('.checkbox-personalizado:checked');
  let dataToSend = [];
  let hoje = new Date();
  
  hoje.setHours(0, 0, 0, 0);

  for (let checkbox of selectedRows) {
    let row = checkbox.closest('.row-lancamentos');
    let id = checkbox.getAttribute('data-id');

    let campoData = document.getElementById(`data-liquidacao-${id}`);
    let dataLiquidacao = new Date(campoData.value);
    if (dataLiquidacao > hoje) {
      alert('A data de liquidação não pode ser maior do que hoje.');
      campoData.focus();
      return;
    }

    let botaoParcial = document.getElementById(`botao-parcial-${id}`);
    let partialAmountField = document.getElementById(`amount-parcial-liquidacao-${id}`);
    let partialAmount = 0;

    if (partialAmountField && partialAmountField.value) {
      // Remover o prefixo 'R$ ' e todos os pontos usados como separadores de milhar
      let formatedAmount = partialAmountField.value.replace('R$ ', '').replace(/\./g, '');
      // Substituir a vírgula por ponto para o separador decimal
      formatedAmount = formatedAmount.replace(',', '.');
      // Converter para float
      partialAmount = parseFloat(formatedAmount);
    }

    if (botaoParcial.checked && (partialAmount <= 0 || isNaN(partialAmount))) {
      alert('Por favor, preencha o amount parcial para realizar uma liquidação parcial.');
      partialAmountField.focus();
      return;
    }
    
    let totalAmountField = document.getElementById(`amount-liquidacao-${id}`);
    let totalAmount = parseFloat(totalAmountField.value.replace(/\D/g, '').replace(',', '.'));
    if (partialAmount > totalAmount) {
      alert('O amount parcial não pode ser maior que o amount total da liquidação.');
      partialAmountField.focus();
      return;
    }
    
    let observationField = document.getElementById(`observation-liquidacao-${id}`);


    let itemData = {
      id: id,
      due_date: row.querySelector('.due_date-row').textContent,
      description: row.querySelector('.description-row').textContent,
      observation: observationField ? observationField.value : '',
      amount: totalAmountField.value,
      general_ledger_account: row.getAttribute('data-general-ledger-account'),
      uuid_general_ledger_account: row.getAttribute('data-uuid-general-ledger-account'),
      current_installment: row.getAttribute('current-installment'),
      total_installments: row.getAttribute('total-installments'),
      transaction_type: row.querySelector('.debito-row').textContent ? 'Débito' : 'Crédito',
      data_liquidacao: campoData ? campoData.value : '',
      banco_liquidacao: nomeBancoSelecionado,
      banco_id_liquidacao: idBancoSelecionado,
      partial_amount: partialAmount > 0 ? partialAmount : undefined,
    };

    dataToSend.push(itemData);
  }

  if (dataToSend.length > 0) {
    try {
      const response = await fetch('/fluxo_de_caixa/processar_liquidacao/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dataToSend)
      });
      const data = await response.json();

      if (data.status === 'success') {
        window.location.reload();
      } else {
        console.error('Operação não foi bem-sucedida:', data);
      }
    } catch (error) {
      console.error('Erro na operação:', error);
    }
  }
});



// Selecionar uma checkbox de cada vez no modal de liquidação
document.addEventListener('DOMContentLoaded', function() {
  // Seleciona todas as checkboxes dentro da tabela de bancos para liquidação
  const checkboxes = document.querySelectorAll('.checkbox-personalizado-liquidacao');

  // Adiciona um ouvinte de eventos a cada checkbox
  checkboxes.forEach(function(checkbox) {
      checkbox.addEventListener('change', function() {
          // Quando uma checkbox é marcada, desmarca todas as outras
          if (this.checked) {
              checkboxes.forEach(function(box) {
                  // Desmarca todas as checkboxes exceto a que acionou o evento
                  if (box !== checkbox) {
                      box.checked = false;
                  }
              });
              // Após ajustar as checkboxes, atualiza o saldo
              atualizarSaldoBanco();
          }
      });
  });
});


// Mobile Buttons
function toggleFilters() {
  var formulario = document.getElementById('formulario-filtros');
  formulario.classList.toggle('show-filters');
}

function toggleBanks() {
  var formulario = document.getElementById('box-grid-bancos');
  formulario.classList.toggle('show-filters');
}

function toggleNav() {
  var navBar = document.querySelector('.nav-bar');
  if (navBar.style.left === '0px') {
      navBar.style.left = '-100%';
  } else {
      navBar.style.left = '0px';
  }
}

// Apagar lançamentos da Tabela
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('apagar-button').addEventListener('click', function() {
      var idsSelecionados = [];
      var checkboxesSelecionadas = document.querySelectorAll('.checkbox-personalizado:checked');
      checkboxesSelecionadas.forEach(function(checkbox) {
          idsSelecionados.push(checkbox.getAttribute('data-id'));
      });

      fetch('/fluxo_de_caixa/deletar_entradas/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken()
          },
          body: JSON.stringify({ids: idsSelecionados})
      })
      .then(response => {
          if (!response.ok) {
              throw response;
          }
          return response.json();
      })
      .then(data => {
          if (data.status === 'success') {
              checkboxesSelecionadas.forEach(function(checkbox) {
                  var linhaParaRemover = checkbox.closest('tr');
                  linhaParaRemover.remove();
              });
              window.location.reload();
          } else {
              // Trata casos em que a operação não é bem-sucedida
              alert(data.message); // Exibe a mensagem de erro do servidor
              // Desmarca todas as checkboxes selecionadas
              desmarcarCheckboxes(checkboxesSelecionadas);
          }
      })
      .catch(error => {
          error.json().then(errorMessage => {
              console.error('Erro:', errorMessage);
              alert(errorMessage.message); // Exibe a mensagem de erro para o usuário
              // Desmarca todas as checkboxes selecionadas
              desmarcarCheckboxes(checkboxesSelecionadas);
          });
      });
  });
});

function getCsrfToken() {
  return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

function desmarcarCheckboxes(checkboxes) {
  checkboxes.forEach(function(checkbox) {
      checkbox.checked = false;
  });
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
  const checkboxes = document.querySelectorAll('.checkbox-personalizado');
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
      
      
// Modais
// Função auxiliar para resetar campos específicos de cada modal
function resetModalFields(formSelector, dropdownId = '', tagInputId = '', tagsHiddenInputId = '', tagContainerId = '') {
  const form = document.querySelector(formSelector);
  form?.reset();

  // Reset do botão dropdown e checkboxes de contas contábeis
  if (dropdownId) {
    const dropdownBtn = document.getElementById(dropdownId);
    dropdownBtn.textContent = 'Selecione';
    document.querySelectorAll(`#${dropdownId}-content .conta-checkbox`).forEach(checkbox => checkbox.checked = false);
  }

  // Reset dos inputs de tags
  const tagInput = document.getElementById(tagInputId);
  if (tagInput) {
    tagInput.value = '';
  }
  
  // Reset do contêiner de tags
  const tagContainer = document.getElementById(tagContainerId);
  while (tagContainer && tagContainer.firstChild) {
    tagContainer.removeChild(tagContainer.firstChild);
  }

  // Reset do input oculto que armazena as tags serializadas
  const tagsHiddenInput = document.getElementById(tagsHiddenInputId);
  if (tagsHiddenInput) {
    tagsHiddenInput.value = '';
  }
}

// Função unificada para manipular a abertura e fechamento de modais
function handleModal(openBtnSelector, modalSelector, formSelector, config = {}) {
  const openBtn = document.querySelector(openBtnSelector);
  const modal = document.querySelector(modalSelector);

  openBtn.addEventListener('click', () => {
    modal.showModal();
    document.body.style.overflow = 'hidden';
  });
  
  openBtn.addEventListener('click', () => {
    modal.showModal();
    document.body.classList.add('modal-open');
  });

  // Fechamento do modal
  const closeModalFunc = () => {
    modal.close();
    document.body.style.overflow = '';
    document.body.classList.remove('modal-open');
    resetModalFields(formSelector, config.dropdownId, config.tagInputId, config.tagsHiddenInputId, config.tagContainerId);
  };

  const closeBtn = document.querySelector(config.closeBtnSelector);
  closeBtn?.addEventListener('click', closeModalFunc);
  modal.addEventListener('keydown', (e) => e.key === 'Escape' && closeModalFunc());
  modal.addEventListener('close', closeModalFunc);
}

document.addEventListener('DOMContentLoaded', () => {
  // Configurações dos modais
  const modalConfigs = [
    {openBtn: '.recebimentos', modal: '.modal-recebimentos', form: '.modal-form-recebimentos', config: {closeBtnSelector: '.modal-fechar-recebimentos', dropdownId: 'dropdown-button-contas-recebimentos', tagInputId: 'tagInput-recebimentos', 
    tagsHiddenInputId: 'tagsHiddenInput-recebimentos', tagContainerId: 'tag-container-recebimentos'}},
    {openBtn: '.pagamentos', modal: '.modal-pagamentos', form: '.modal-form-pagamentos', config: {closeBtnSelector: '.modal-fechar-pagamentos', dropdownId: 'dropdown-button-contas-pagamentos', tagInputId: 'tagInput-pagamentos', 
    tagsHiddenInputId: 'tagsHiddenInput-recebimentos', tagContainerId: 'tag-container-pagamentos'}},
    {openBtn: '.transferencias', modal: '.modal-transferencias', form: '.modal-form-transferencias', config: {closeBtnSelector: '.modal-fechar-transferencias'}},
    {openBtn: '.liquidar-button', modal: '.modal-liquidacoes', form: '.modal-form-liquidacoes', config: {closeBtnSelector: '.modal-fechar-liquidacoes'}},
  ];

  // Aplicar configurações para cada modal
  modalConfigs.forEach(({openBtn, modal, form, config}) => {
    handleModal(openBtn, modal, form, config);
  });
});

document.querySelectorAll('.conta-checkbox').forEach(checkbox => {
  checkbox.addEventListener('change', function() {
    if (this.checked) {
      // Determinar se é um recebimento ou pagamento
      const isRecebimento = this.name === "contas_recebimentos";
      const uuidFieldId = isRecebimento ? "general_ledger_account_uuid_recebimentos" : "general_ledger_account_uuid_pagamentos";
      const nomeFieldId = isRecebimento ? "general_ledger_account_nome_recebimentos" : "general_ledger_account_nome_pagamentos";
      
      // Atualizar campos ocultos
      document.getElementById(uuidFieldId).value = this.dataset.uuidAccount;
      document.getElementById(nomeFieldId).value = this.dataset.account;
    }
  });
});


// Evento para editar lançamentos ao clicar duas vezes nas células da tabela
let estaEditando = false;

// Event Listeners Principais
document.addEventListener('DOMContentLoaded', function() {
  configurarEventos();
});

function configurarEventos() {
  document.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
          fecharModais();
      }
  });
  ['recebimentos', 'pagamentos'].forEach(tipo => {
      document.getElementById(`modal-${tipo}`).onclose = function() {
          onModalClose(tipo);
      };
  });
  configurarEventosTabela();
}

function configurarEventosTabela() {
  const cells = document.querySelectorAll('.row-lancamentos td:not(.checkbox-row)');
  cells.forEach(cell => {
    cell.addEventListener('dblclick', function() {
      handleCellDoubleClick(this);
    });
  });
}

// Funções de Eventos de Tabela
function handleCellDoubleClick(cell) {
  if (!cell.classList.contains('checkbox-row')) {
    const row = cell.closest('.row-lancamentos');
    abrirModalEdicao(row);
  }
}

// Funções de Manipulação de Modais
function abrirModalEdicao(row) {
  const transaction_type = row.getAttribute('data-transaction-type');
  const tipo = transaction_type === 'Crédito' ? 'recebimentos' : 'pagamentos';
  abrirModalEdicaoGeral(row, tipo);
}

function abrirModalEdicaoGeral(row, tipo) {
  estaEditando = true;
  preencherDadosModal(row, tipo);
  showInstallments(row, tipo);
  const modal = document.getElementById(`modal-${tipo}`);
  modal.showModal();
}

function fecharModais() {
  ['recebimentos', 'pagamentos'].forEach(tipo => {
      const modal = document.getElementById(`modal-${tipo}`);
      if (modal.open) {
          const form = document.querySelector(`.modal-form-${tipo}`);
          form.reset();
          modal.close();
      }
  });
}
  
function onModalClose(tipo) {
  configurarCamposAtivos(tipo, true);
  limparCamposModal(tipo);
  estaEditando = false;
  redefineInstallmentsField(tipo);
  document.getElementById(`amount-${tipo}`).value = "R$ "
}

function limparCamposModal(tipo) {
  const inputs = document.querySelectorAll(`.modal-form-${tipo} input`);
  inputs.forEach(input => {
      if (input.type !== 'submit' && input.name !== 'csrfmiddlewaretoken') {
          input.value = '';
      }
  });
}

// Função auxiliar para ativar ou desativar campos
function configurarCamposAtivos(tipo, ativar) {
  const campos = {
    amount: document.getElementById(`amount-${tipo}`),
    recorrencia: document.getElementById(`recorrencia-${tipo}`),
    dropdownButton: document.getElementById(`dropdown-button-contas-${tipo}`),
    checkboxes: document.querySelectorAll(`#dropdown-content-contas-${tipo} .conta-checkbox`)
  };

  if (ativar) {
    campos.amount.readOnly = false;
    configurarElemento(campos.amount, { backgroundColor: '', color: '', cursor: '' });
    campos.recorrencia.disabled = false;
    configurarElemento(campos.recorrencia, { backgroundColor: '', color: '', cursor: '' });
    campos.dropdownButton.disabled = false;
    configurarElemento(campos.dropdownButton, { backgroundColor: '', color: '', cursor: '' });
    campos.checkboxes.forEach(checkbox => checkbox.disabled = false);
  } else {
    campos.amount.readOnly = true;
    configurarElemento(campos.amount, { backgroundColor: '#B5B5B5', color: '#FFFFFF', cursor: 'default' });
    campos.recorrencia.disabled = true;
    configurarElemento(campos.recorrencia, { backgroundColor: '#B5B5B5', color: '#FFFFFF', cursor: 'default' });
    campos.dropdownButton.disabled = true;
    configurarElemento(campos.dropdownButton, { backgroundColor: '#B5B5B5', color: '#FFFFFF', cursor: 'default' });
    campos.checkboxes.forEach(checkbox => checkbox.disabled = true);
  }
}

function configurarElemento(elemento, propriedades) {
  Object.keys(propriedades).forEach(prop => {
    elemento.style[prop] = propriedades[prop];
  });
}

function preencherDadosModal(row, tipo) {
  const originalTotalInstallments = row.getAttribute('total-installments');
  document.getElementById(`total-installments-originais-${tipo}`).value = originalTotalInstallments;

  const due_date = row.querySelector('.due_date-row').textContent.trim();
  document.getElementById(`data-${tipo}`).value = formatarDataParaInput(due_date);

  const amount = row.querySelector(`.${tipo === 'recebimentos' ? 'credito' : 'debito'}-row`).textContent.trim();
  document.getElementById(`amount-${tipo}`).value = "R$ " + amount;

  document.getElementById(`description-${tipo}`).value = row.querySelector('.description-row').textContent.trim();
  document.getElementById(`observation-${tipo}`).value = row.querySelector('.observation-row').childNodes[0].textContent.trim();

  const tagsString = extrairTags(row);
  adicionarTagsAoContainer(tagsString, tipo);

  const generalLedgerAccount = row.getAttribute('data-general-ledger-account');
  document.getElementById(`general_ledger_account_nome_${tipo}`).value = generalLedgerAccount;
  selectGeneralLedgerAccountDropdown(tipo, generalLedgerAccount);

  const uuidGeneralLedgerAccount = row.getAttribute('data-uuid-general-ledger-account');
  document.getElementById(`general_ledger_account_uuid_${tipo}`).value = uuidGeneralLedgerAccount;
  selectGeneralLedgerAccountDropdown(tipo, uuidGeneralLedgerAccount);

  const lancamentoId = row.querySelector('.checkbox-personalizado').getAttribute('data-id');
  document.querySelector(`[name="lancamento_id_${tipo}"]`).value = lancamentoId;

  const uuid = row.getAttribute('data-uuid-row');
  configurarCamposAtivos(tipo, uuid === 'None');
}

function selectGeneralLedgerAccountDropdown(tipo, uuidGeneralLedgerAccount) {
  const checkboxesGeneralLedgerAccount = document.querySelectorAll(`#dropdown-content-contas-${tipo} .conta-checkbox`);
  checkboxesGeneralLedgerAccount.forEach(checkbox => {
    if (checkbox.dataset.uuidAccount === uuidGeneralLedgerAccount) {
      checkbox.checked = true;
      document.getElementById(`dropdown-button-contas-${tipo}`).textContent = checkbox.dataset.account;
    } else {
      checkbox.checked = false;
    }
  });
}

// Função para mostrar campo de recorrência
function showInstallments(row, tipo) {
  const select = document.getElementById(`recorrencia-${tipo}`);
  const section = document.getElementById(`parcelas-section-${tipo}`);
  const input = document.getElementById(`parcelas-${tipo}`);

  section.style.display = select.value === 'sim' ? 'block' : 'none';
  if (estaEditando) {
      const totalInstallments = row.getAttribute('total-installments') ? parseInt(row.getAttribute('total-installments')) : 1;
      const currentInstallment = row.getAttribute('current-installment') ? parseInt(row.getAttribute('current-installment')) : 1;
      input.value = currentInstallment;
      input.disabled = totalInstallments > 1;
  } else {
      input.value = select.value === 'sim' ? '' : '1';
      input.disabled = false;
  }
}

function adicionarTagsAoContainer(tagsString, tipo) {
  const containerId = `tag-container-${tipo}`;
  const hiddenInputId = `tagsHiddenInput-${tipo}`;
  const tagContainer = document.getElementById(containerId);
  while (tagContainer.firstChild) {
      tagContainer.removeChild(tagContainer.firstChild);
  }
  const tags = tagsString.split(',');
  tags.forEach(tag => {
      if (tag.trim()) {
          addTag(tag.trim(), containerId, hiddenInputId);
      }
  });
}

function redefineInstallmentsField(tipo) {
  var select = document.getElementById(`recorrencia-${tipo}`);
  var input = document.getElementById(`parcelas-${tipo}`);
  var section = document.getElementById(`parcelas-section-${tipo}`);

  section.style.display = select.value === 'sim' ? 'block' : 'none';
  input.value = select.value === 'sim' ? '' : '1';
  input.disabled = false;
}

// Funções de Formatação e Utilidades
function desformatarNumero(formatedAmount) {
  return formatedAmount.replace(/\./g, '').replace(',', '.');
}

function formatarDataParaInput(data) {
  const partes = data.split('/');
  return partes.reverse().join('-');
}

function simularEnter(elementId) {
  const event = new KeyboardEvent('keydown', {'key': 'Enter'});
  document.getElementById(elementId).dispatchEvent(event);
}

function extrairTags(row) {
  const tagsContainer = row.querySelector('.d-block');
  return tagsContainer ? tagsContainer.textContent.trim().replace(/^Tags:\s*/, '') : '';
}


// Função para formatar o amount de um campo como moeda brasileira
function formatAmount(input) {
  let numericAmount = input.value.replace(/\D/g, '');
  let floatAmount = parseFloat(numericAmount) / 100;
  let formatedAmount = floatAmount.toFixed(2)
    .replace('.', ',')
    .replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  input.value = numericAmount ? `R$ ${formatedAmount}` : 'R$ 0,00';
  if (input.value === 'R$ 0,00') {
    input.value = 'R$ 0,00';
  }
}


// Verifica se a tecla 'Shift' foi pressionada juntamente com 'D'
document.addEventListener('keydown', function(event) {
  if (event.shiftKey && event.key === 'D') {
      var elementoFocado = document.activeElement;
      if (elementoFocado && elementoFocado.type === 'date') {
          var dataAtual = new Date().toISOString().split('T')[0];
          elementoFocado.value = dataAtual;
          event.preventDefault();
          moverParaProximoCampo(elementoFocado);
      }
  }
});

function moverParaProximoCampo(campoAtual) {
  var form = campoAtual.form;
  var index = Array.prototype.indexOf.call(form, campoAtual) + 1; // Começa no próximo elemento
  var proximoCampo;

  // Percorre os campos subsequentes do formulário até encontrar um que seja editável
  while (index < form.elements.length) {
      proximoCampo = form.elements[index];
      if (proximoCampo && !proximoCampo.disabled && !proximoCampo.readOnly && !proximoCampo.hidden && proximoCampo.tabIndex >= 0) {
          proximoCampo.focus();
          break; // Sai do loop assim que encontra um campo editável
      }
      index++; // Move para o próximo campo no formulário
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

initializeTagInputs('tagInput-recebimentos', 'tag-container-recebimentos', 'tagsHiddenInput-recebimentos');
initializeTagInputs('tagInput-pagamentos', 'tag-container-pagamentos', 'tagsHiddenInput-pagamentos');


// Soma de amounts no campo de liquidar
function calcularTotal() {
  let total = 0;

  // Somar os amounts apenas das linhas com checkboxes selecionadas
  document.querySelectorAll('.row-lancamentos').forEach(row => {
      const checkbox = row.querySelector('.checkbox-personalizado');

      if (checkbox && checkbox.checked) {
          const credito = row.querySelector('.credito-row').textContent.trim();
          const debito = row.querySelector('.debito-row').textContent.trim();

          if (credito) {
              total += formatAmount(credito);
          }

          if (debito) {
              total -= formatAmount(debito);
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

function formatAmountBalance(strAmount) {
  // Remove pontos e substitui vírgula por ponto para conversão para número
  return parseFloat(strAmount.replace(/\./g, '').replace(',', '.'));
}

// Adicionar evento listener para as checkboxes para recalcular o total quando uma checkbox é alterada
document.querySelectorAll('.checkbox-personalizado').forEach(checkbox => {
  checkbox.addEventListener('change', calcularTotal);
});

// Chamar a função calcularTotal inicialmente
calcularTotal();


// Filtro de meses
const config = {
  meses: ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'],
  today: new Date(),
};

function getCurrentMonthIndex() {
  return config.today.getMonth();
}

function getCurrentYear() {
  return config.today.getFullYear();
}

function marcarMesesAnterioresAteAtual(index, currentYear) {
  const checkboxesMeses = document.querySelectorAll('#dropdown-content-meses .mes-checkbox');
  checkboxesMeses.forEach(checkbox => {
    const [mesCheckbox, anoCheckbox] = checkbox.value.split('/');
    const mesIndex = config.meses.indexOf(mesCheckbox);
    const ano = parseInt(anoCheckbox, 10);
    checkbox.checked = (ano < currentYear) || (ano === currentYear && mesIndex <= index);
  });
  updateButtonTextMeses();
  filterTable();
}

function encontrarEMarcarMesAtualOuProximo() {
  let currentMonthIndex = getCurrentMonthIndex();
  let currentYear = getCurrentYear();
  const checkboxesMeses = document.querySelectorAll('#dropdown-content-meses .mes-checkbox');

  for (let tentativas = 0; tentativas < 12; tentativas++) {
    const mesAnoProcurado = `${config.meses[currentMonthIndex]}/${currentYear}`;
    const encontrado = [...checkboxesMeses].some(checkbox => checkbox.value === mesAnoProcurado);

    if (encontrado) {
      marcarMesesAnterioresAteAtual(currentMonthIndex, currentYear);
      return;
    }

    currentMonthIndex = (currentMonthIndex + 1) % 12;
    if (currentMonthIndex === 0) currentYear++;
  }

  console.error('Nenhum mês válido encontrado. Considere revisar os amounts dos checkboxes.');
}

document.addEventListener('DOMContentLoaded', encontrarEMarcarMesAtualOuProximo);

// Adiciona listeners para checkboxes
function addListenerAndUpdate(selector, updateFunction, filterFunction = null, isExclusive = false) {
  document.querySelectorAll(selector).forEach(checkbox => {
    checkbox.addEventListener('change', function() {
      if (isExclusive && checkbox.checked) {
        // Se é exclusivo e a checkbox é selecionada, desmarque todas as outras
        document.querySelectorAll(selector).forEach(box => {
          if (box !== checkbox) box.checked = false;
        });
      }
      // A função de atualização é chamada após um atraso se necessário
      if (selector.includes('recebimentos') || selector.includes('pagamentos')) {
        setTimeout(updateFunction, 0);
      } else {
        updateFunction();
      }
      // Chama a função de filtragem se for fornecida
      if (filterFunction) {
        filterFunction();
      }
    });
  });
}

// Adicionando os listeners para cada grupo de checkboxes
addListenerAndUpdate('#dropdown-content-contas .conta-checkbox', updateButtonTextContas, filterTable);
addListenerAndUpdate('#dropdown-content-meses .mes-checkbox', updateButtonTextMeses, filterTable);
addListenerAndUpdate('#dropdown-content-bancos .banco-checkbox', updateButtonTextBancos, filtrarBancos);
addListenerAndUpdate('#dropdown-content-transaction_type .transaction_type-checkbox', updateButtonTextTransactionType, filterTable);
addListenerAndUpdate('#dropdown-content-contas-recebimentos .conta-checkbox', updateButtonTextContasRecebimentos, null, true);
addListenerAndUpdate('#dropdown-content-contas-pagamentos .conta-checkbox', updateButtonTextContasPagamentos, null, true);

// Adiciona o listener para click fora do dropdown
document.addEventListener('click', function(event) {
  const dropdowns = [
      {button: "#dropdown-button-contas", content: "dropdown-content-contas"},
      {button: "#dropdown-button-meses", content: "dropdown-content-meses"},
      {button: "#dropdown-button-bancos", content: "dropdown-content-bancos"},
      {button: "#dropdown-button-transaction_type", content: "dropdown-content-transaction_type"},
      {button: "#dropdown-button-contas-recebimentos", content: "dropdown-content-contas-recebimentos"},
      {button: "#dropdown-button-contas-pagamentos", content: "dropdown-content-contas-pagamentos"}
  ];

  dropdowns.forEach(function(dropdown) {
      if (!event.target.closest(dropdown.button) && !event.target.closest(`#${dropdown.content}`)) {
          const content = document.getElementById(dropdown.content);
          if (content && content.classList.contains('show')) {
              content.classList.remove('show');
          }
      }
  });
});

// Funções para manipular os eventos de abertura dos dropdowns
function toggleDropdownFilters(dropdownId, event) {
  event.stopPropagation();
  const dropdown = document.getElementById(dropdownId);
  dropdown.classList.toggle("show");
}

function toggleDropdownModals(dropdownId, event) {
  event.stopPropagation();
  const dropdown = document.getElementById(dropdownId);
  const buttonRect = event.target.getBoundingClientRect();

  if (dropdown.classList.contains("show")) {
    // Hide the dropdown
    dropdown.classList.remove("show");
    // Reset styles
    Object.assign(dropdown.style, {
      maxHeight: null,
      position: null,
      top: null,
      left: null,
      overflowY: null
    });
  } else {
    // Show the dropdown and adjust its position and styles
    dropdown.classList.add("show");
    Object.assign(dropdown.style, {
      position: 'fixed',
      left: `${window.scrollX + buttonRect.left}px`,
      maxHeight: '250px',
      overflowY: 'auto'
    });
  }
}

// Funções para selecionar e desmarcar todos os checkboxes
function toggleAllCheckboxes(containerSelector, shouldCheck) {
  const checkboxes = document.querySelectorAll(`${containerSelector} .dropdown-options input[type="checkbox"]`);
  checkboxes.forEach(checkbox => checkbox.checked = shouldCheck);
  
  // Atualiza o texto do botão e filtra a tabela conforme o container
  switch (containerSelector) {
    case '#dropdown-content-contas':
      updateButtonTextContas();
      filterTable();
      break;
    case '#dropdown-content-meses':
      updateButtonTextMeses();
      filterTable();
      break;
    case '#dropdown-content-bancos':
      updateButtonTextBancos();
      filtrarBancos();
      break;
    case '#dropdown-content-transaction_type':
      updateButtonTextTransactionType();
      filterTable();
      break;
  }
}

// Função para atualizar o texto dos botões de dropdown
function updateButtonText(dropdownId, checkboxesSelector, defaultText, allSelectedText = "Todos Selecionados") {
  const selectedCount = document.querySelectorAll(`${checkboxesSelector}:checked`).length;
  const totalOptions = document.querySelectorAll(checkboxesSelector).length;
  const buttonText = selectedCount === 0 ? defaultText : 
                     selectedCount === totalOptions ? allSelectedText : 
                     `${selectedCount} Selecionado(s)`;
  document.getElementById(dropdownId).textContent = buttonText;
}

// Chamadas específicas para cada dropdown
function updateButtonTextContas() {
  updateButtonText('dropdown-button-contas', '#dropdown-content-contas .conta-checkbox', 'Selecione');
}

function updateButtonTextMeses() {
  updateButtonText('dropdown-button-meses', '#dropdown-content-meses .mes-checkbox', 'Selecione');
}

function updateButtonTextBancos() {
  updateButtonText('dropdown-button-bancos', '#dropdown-content-bancos .banco-checkbox', 'Selecione');
}

function updateButtonTextTransactionType() {
  const checkboxes = document.querySelectorAll('#dropdown-content-transaction_type .transaction_type-checkbox');
  const selectedCheckboxes = document.querySelectorAll('#dropdown-content-transaction_type .transaction_type-checkbox:checked');
  const selectedCount = selectedCheckboxes.length;
  const totalOptions = checkboxes.length;
  let buttonText = "Crédito, Débito";
  if (selectedCount > 0 && selectedCount < totalOptions) {
    buttonText = Array.from(selectedCheckboxes).map(cb => cb.nextSibling.textContent.trim()).join(", ");
  }
  document.getElementById('dropdown-button-transaction_type').textContent = buttonText;
}

// Chamadas para contas de recebimentos e pagamentos
function updateButtonTextContasRecebimentos() {
  const selectedCheckbox = document.querySelector('#dropdown-content-contas-recebimentos .conta-checkbox:checked');
  const selectedText = selectedCheckbox ? selectedCheckbox.nextSibling.textContent.trim() : "Selecione";
  document.getElementById('dropdown-button-contas-recebimentos').textContent = selectedText;
}

function updateButtonTextContasPagamentos() {
  const selectedCheckbox = document.querySelector('#dropdown-content-contas-pagamentos .conta-checkbox:checked');
  const selectedText = selectedCheckbox ? selectedCheckbox.nextSibling.textContent.trim() : "Selecione";
  document.getElementById('dropdown-button-contas-pagamentos').textContent = selectedText;
}

// Filtros
function filterTable() {
  const uuidsGeneralLedgerAccountFilter = Array.from(document.querySelectorAll('#dropdown-content-contas .conta-checkbox:checked')).map(checkbox => checkbox.value);
  const monthsIntervalFilter = Array.from(document.querySelectorAll('#dropdown-content-meses .mes-checkbox:checked')).map(checkbox => ({
    start: new Date(checkbox.getAttribute('data-start-of-month')),
    end: new Date(checkbox.getAttribute('data-end-of-month'))
  }));
  const transactionTypeFilter = Array.from(document.querySelectorAll('#dropdown-content-transaction_type .transaction_type-checkbox:checked'), cb => cb.value);

  // Verificações de seleção total ou nenhuma seleção simplificadas
  const selectAllMonths = monthsIntervalFilter.length === 0;
  const selectAllTransactionType = transactionTypeFilter.length === 0;

  // Obtenção dos filtros de texto e datas
  const descriptionFilter = document.getElementById("caixa-pesquisa").value.toUpperCase();
  const tagsFilter = document.getElementById("caixa-pesquisa-tags").value.toUpperCase();
  const startDateObj = document.getElementById("data-inicio").value ? new Date(document.getElementById("data-inicio").value) : null;
  const endDateObj = document.getElementById("data-fim").value ? new Date(document.getElementById("data-fim").value) : null;
  let visibleMonthsYears = new Set();

  document.querySelectorAll("#tabela-lancamentos .row-lancamentos").forEach(row => {
    const uuidGeneralLedgerAccount = row.getAttribute('data-uuid-general-ledger-account');
    const description = row.querySelector(".description-row").textContent.toUpperCase();
    const observationElement = row.querySelector(".observation-row").cloneNode(true);
    const tagsObj = observationElement.querySelector(".d-block");
    if (tagsObj) observationElement.removeChild(tagsObj);
    const observation = observationElement.textContent.toUpperCase();
    const tags = tagsObj ? tagsObj.textContent.toUpperCase() : "";
    const dueDate = new Date(row.querySelector(".due_date-row").textContent.split('/').reverse().join('-'));
    const transactionType = row.getAttribute('data-transaction-type');

    // Centraliza a lógica de correspondência
    const generalLedgerAccountMatch = uuidsGeneralLedgerAccountFilter.length === 0 || uuidsGeneralLedgerAccountFilter.includes(uuidGeneralLedgerAccount);
    const descriptionObservationMatch = descriptionFilter === "" || description.includes(descriptionFilter) || observation.includes(descriptionFilter);
    const tagMatch = tagsFilter === "" || tags.includes(tagsFilter);
    const monthMatch = selectAllMonths || monthsIntervalFilter.some(intervalo => dueDate >= intervalo.start && dueDate <= intervalo.end);
    const dataMatch = (!startDateObj || dueDate >= startDateObj) && (!endDateObj || dueDate <= endDateObj);
    const transactionTypeMatch = selectAllTransactionType || transactionTypeFilter.includes(transactionType);

    row.style.display = descriptionObservationMatch && tagMatch && monthMatch && transactionTypeMatch && dataMatch && generalLedgerAccountMatch ? "" : "none";

    if (row.style.display === "") {
      let mesAno = dueDate.toLocaleString('default', { month: '2-digit', year: 'numeric' });
      visibleMonthsYears.add(mesAno);
    }
  });

  // Simplificação na filtragem das linhas de total do mês
  document.querySelectorAll("#tabela-lancamentos .linha-total-mes").forEach(row => {
    let textoMesAno = row.querySelector("td:nth-child(2)").textContent;
    let mesAnoMatch = textoMesAno.match(/\d{2}\/\d{4}$/); // Captura MM/YYYY
    row.style.display = mesAnoMatch && visibleMonthsYears.has(mesAnoMatch[0]) ? "" : "none";
  });

  calcularSaldoAcumulado();
}

// Event listeners para os elementos de filtro
document.getElementById('caixa-pesquisa').addEventListener('keyup', filterTable);
document.getElementById('caixa-pesquisa-tags').addEventListener('keyup', filterTable);
document.getElementById('data-inicio').addEventListener('change', filterTable);
document.getElementById('data-fim').addEventListener('change', filterTable);

// Calcula o saldo total dos bancos, sem filtragem
document.addEventListener("DOMContentLoaded", function() {
  atualizarSaldoTotalBancos();
});

function atualizarSaldoTotalBancos() {
  var linhasBanco = document.querySelectorAll(".row-bancos");
  var saldoTotal = 0;

  linhasBanco.forEach(function(row) {
    var celulaSaldo = row.querySelector(".saldo-banco-row");
    if (celulaSaldo) {
      var saldo = parseSaldo(celulaSaldo.textContent);
      saldoTotal += saldo;
    }
  });

  // Formata o saldo total como moeda
  var saldoFormatado = formatarComoMoeda(saldoTotal);

  // Atualiza o saldo total na interface do usuário
  var saldoTotalBancoRow = document.querySelector(".saldo-total-banco-row");
  if (saldoTotalBancoRow) {
    saldoTotalBancoRow.textContent = saldoFormatado;
  }

  // Atualiza o saldo total no campo de liquidação
  var saldoTotalBancoLiquidacaoRow = document.querySelector(".saldo-total-banco-liquidacao-row");
  if (saldoTotalBancoLiquidacaoRow) {
    saldoTotalBancoLiquidacaoRow.textContent = saldoFormatado;
  }

  // Atualizar os saldos do fluxo de caixa com o novo saldo total
  atualizarSaldosFluxoCaixa(saldoTotal);
}

// Função para atualizar os saldos do fluxo de caixa
function atualizarSaldosFluxoCaixa(saldoInicial) {
  var linhasFluxoCaixa = document.querySelectorAll("#tabela-lancamentos .row-lancamentos");
  var saldoAtual = saldoInicial;

  linhasFluxoCaixa.forEach(function(row) {
    var debitoCelula = row.querySelector(".debito-row");
    var creditoCelula = row.querySelector(".credito-row");
    var debito = debitoCelula && debitoCelula.textContent ? parseSaldo(debitoCelula.textContent) : 0;
    var credito = creditoCelula && creditoCelula.textContent ? parseSaldo(creditoCelula.textContent) : 0;
    
    saldoAtual += credito - debito;
    
    var saldoCelula = row.querySelector(".saldo-row");
    if (saldoCelula) {
      saldoCelula.textContent = formatarComoMoeda(saldoAtual);
    }
    else {
      row.style.display = "none"; 
    }
  });
}

// Calcular o saldo total dos bancos que estão sendo filtrados
function filtrarBancos() {
  console.log
  var checkboxesBancosSelecionados = document.querySelectorAll('.dropdown-options .banco-checkbox:checked');
  var bancosSelecionados = Array.from(checkboxesBancosSelecionados).map(checkbox => checkbox.value);
  var todosSelecionados = bancosSelecionados.length === 0 || bancosSelecionados.includes('Todos');

  var tabelaBancos = document.getElementById("box-grid-bancos").querySelector("tbody");
  var linhas = tabelaBancos.querySelectorAll(".row-bancos");

  var saldoTotal = 0;

  linhas.forEach(row => {
      var bancoLinhaId = row.getAttribute("data-banco-id");
      
      if (todosSelecionados || bancosSelecionados.includes(bancoLinhaId)) {
          row.style.display = ""; // Mostra a linha
          var saldoBanco = parseSaldo(row.querySelector(".saldo-banco-row").textContent);
          saldoTotal += saldoBanco;
      } else {
          row.style.display = "none"; // Esconde a linha
      }
  });

  var saldoTotalBancoRow = document.querySelector(".saldo-total-banco-row");
  if (saldoTotalBancoRow) {
      saldoTotalBancoRow.textContent = formatarComoMoeda(saldoTotal);
  }

  // Agora atualizarSaldosFluxoCaixa é chamada dentro do escopo de filtrarBancos
  // Remova ou comente esta linha se não deseja atualizar saldos de fluxo de caixa baseado na filtragem de bancos
atualizarSaldosFluxoCaixa(saldoTotal);
}

// Calcular saldo no fluxo de caixa
function calcularSaldoAcumulado() {
  // Obtem o saldo inicial total dos bancos.
  var saldoTotalBancoRow = document.querySelector(".saldo-total-banco-row");
  var saldoInicial = saldoTotalBancoRow ? parseSaldo(saldoTotalBancoRow.textContent) : 0;
  var saldoAtual = saldoInicial;
  
  // Seleciona todas as linhas visíveis do fluxo de caixa.
  var linhasFluxoCaixa = document.querySelectorAll("#tabela-lancamentos .row-lancamentos");
  
  linhasFluxoCaixa.forEach(function(row) {
    if (row.style.display !== "none") {
      var debitoCelula = row.querySelector(".debito-row");
      var creditoCelula = row.querySelector(".credito-row");
      var debito = debitoCelula && debitoCelula.textContent ? parseSaldo(debitoCelula.textContent) : 0;
      var credito = creditoCelula && creditoCelula.textContent ? parseSaldo(creditoCelula.textContent) : 0;
      
      // Calcula o saldo atual baseado no saldo anterior, créditos e débitos.
      saldoAtual += credito - debito;
      
      // Atualiza a célula de saldo da linha atual.
      var saldoCelula = row.querySelector(".saldo-row");
      if (saldoCelula) {
        saldoCelula.textContent = formatarComoMoeda(saldoAtual);
      }
    }
  });
}

function parseSaldo(balance) {
  var numero = balance.replace('R$', '').trim().replace(/\./g, '').replace(',', '.');
  return parseFloat(numero) || 0;
}

function formatarComoMoeda(amount) {
  return amount.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

document.querySelectorAll('.saldo-total-row').forEach(function(cell) {
  var saldoTexto = cell.textContent.replace(/\s/g, '');
  var saldo = parseFloat(saldoTexto.replace('.', '').replace(',', '.'));
    if (!isNaN(saldo) && saldo < 0) {
        cell.style.color = '#740000';
    }
    else {
      cell.style.color = '#000acf';
  }
});