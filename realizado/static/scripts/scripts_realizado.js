// Botão de Retornar
document.getElementById('retornar-button').addEventListener('click', function() {
    let selectedRows = document.querySelectorAll('.checkbox-personalizado:checked');
    let dataToSend = [];
    
    selectedRows.forEach(function(checkbox) {
        let row = checkbox.closest('.row-lancamentos');
        let debito = row.querySelector('.debito-row').textContent.trim();
        let credito = row.querySelector('.credito-row').textContent.trim();
        dataToSend.push({
            id: checkbox.getAttribute('data-id'),
            due_date: row.querySelector('.due_date-row').textContent,
            description: row.querySelector('.description-row').textContent,
            totalAmount: debito || credito, // Usa débito se disponível, senão credito
            general_ledger_account: row.getAttribute('data-general-ledger-account'),
            current_installment: row.getAttribute('current-installment'),
            total_installments: row.getAttribute('total-installments'),
            natureza: debito ? 'Débito' : 'Crédito',
            uuid_correlacao: row.getAttribute('data-uuid-correlacao'),
            uuid_correlacao_parcelas: row.getAttribute('data-uuid-correlacao-parcelas')
        });
    });

    fetch('/realizado/processar_retorno/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dataToSend)
    }).then(response => response.json())
      .then(data => {
          if(data.status === 'success') {
              // Remove as linhas da tabela no frontend
              selectedRows.forEach(checkbox => {
                  let row = checkbox.closest('.row-lancamentos');
                  row.remove();
              });
              // Recarrega a página para refletir as mudanças no backend
              window.location.reload();
          }
      }).catch(error => console.error('Erro ao processar retorno:', error));
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
  // Seleciona apenas as checkboxes com a classe '.checkbox-personalizado'
  const checkboxes = document.querySelectorAll('input[type="checkbox"].checkbox-personalizado');
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


document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.row-lancamentos').forEach(row => {
      row.addEventListener('dblclick', function(event) {
          // Verifica se o clique duplo ocorreu dentro de um elemento com a classe 'checkbox-row'
          if (!event.target.closest('.checkbox-row')) {
              abrirModalEdicao(this);
          }
      });
  });

  // Adiciona lógica para fechar o modal e resetar o formulário com a tecla Esc
  document.addEventListener('keydown', function(event) {
      if (event.key === "Escape") {
          const modal = document.getElementById('modal-realizado');
          if (modal.open) {
              fecharModal(modal);
          }
      }
  });
});

function abrirModalEdicao(row) {
  const id = row.getAttribute('data-id-row');
  const due_date = row.querySelector('.due_date-row').textContent.trim();
  const description = row.querySelector('.description-row').textContent.trim();
  const observation = row.querySelector('.observation-row').textContent.split('Tags:')[0].trim().replace(/\s+/g, ' ');
  const totalAmount = row.querySelector('.debito-row').textContent.trim() || row.querySelector('.credito-row').textContent.trim();
  const generalLedgerAccount = row.getAttribute('data-general-ledger-account');
  const tags = row.querySelector('.observation-row').textContent.trim().split('Tags:')[1];
  const parcelaAtual = row.getAttribute('current-installment');
  const parcelasTotal = row.getAttribute('total-installments');
  const uuid = row.getAttribute('data-uuid-correlacao');
  const uuidParcelas = row.getAttribute('data-uuid-correlacao-parcelas');

  preencherDadosModalRealizado(id, due_date, description, observation, totalAmount, generalLedgerAccount, tags, parcelaAtual, parcelasTotal, uuid, uuidParcelas);

  document.getElementById('modal-realizado').showModal();
}

function preencherDadosModalRealizado(id, due_date, description, observation, totalAmount, generalLedgerAccount, tags, parcelaAtual, parcelasTotal, uuid, uuidParcelas) {
  document.querySelector('.modal-form-realizado [name="lancamento_id_realizado"]').value = id;
  document.getElementById('data-realizado').value = formatarDataParaInput(due_date);
  document.getElementById('description-realizado').value = description;
  document.getElementById('observation-realizado').value = observation;
  document.getElementById('amount-realizado').value = "R$ "+ totalAmount;
  document.getElementById('general-ledger-account-realizado').value = generalLedgerAccount;
  document.getElementById('parcelas-realizado').value = `${parcelaAtual}/${parcelasTotal}`;
  document.querySelector('.modal-form-realizado [name="uuid_realizado"]').value = uuid;
  document.querySelector('.modal-form-realizado [name="uuid_parcelas_realizado"]').value = uuidParcelas;

  // Limpa o container de tags antes de adicionar novas
  const tagContainer = document.getElementById('tag-container-realizado');
  tagContainer.innerHTML = '';
  tags && tags.split(',').forEach(tag => {
      if (tag.trim()) {
          adicionarTag(tag.trim(), 'tag-container-realizado');
      }
  });
}

function formatarDataParaInput(data) {
  const [dia, mes, ano] = data.split('/');
  return `${ano}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`;
}


function adicionarTag(tag, containerId) {
  const container = document.getElementById(containerId);
  const tagElement = document.createElement('span');
  tagElement.classList.add('tag');
  tagElement.textContent = tag;
  container.appendChild(tagElement);
}

// Função para fechar o modal e voltar às configurações iniciais
function fecharModal(modal) {
  const form = document.querySelector(".modal-form-realizado");
  document.getElementById('tag-container-realizado').innerHTML = '';
  modal.close();
  form.reset();
}

document.querySelector('.modal-fechar-realizado').addEventListener('click', function() {
  const modal = document.getElementById('modal-realizado');
  fecharModal(modal);
});

// Edição de realizado
document.addEventListener('DOMContentLoaded', function() {
  const formRealizado = document.querySelector('.modal-form-realizado');

  formRealizado.addEventListener('submit', function(e) {
      e.preventDefault(); // Impede a submissão padrão do formulário

      const lancamentoId = document.querySelector('[name="lancamento_id_realizado"]').value;
      const dataRealizado = document.getElementById('data-realizado').value;
      const settledDescription = document.getElementById('description-realizado').value;
      const settledObservation = document.getElementById('observation-realizado').value;
      const uuid = document.querySelector('[name="uuid_realizado"]').value;
      const uuidParcelas = document.querySelector('[name="uuid_parcelas_realizado"]').value;

      const hoje = new Date();
      const dataRealizadoDate = new Date(dataRealizado);
      hoje.setHours(0, 0, 0, 0);

      if (dataRealizadoDate > hoje) {
          alert('A data não pode ser futura. Por favor, selecione a data de hoje ou uma anterior.');
          return;
      }

      if (uuid !== 'None' && uuidParcelas === 'None') {
        atualizarDataLancamentosRelacionados(uuid, dataRealizado)
            .then(response => response.json()) // Garantir que estamos processando a resposta como JSON
            .then(data => {
                console.log('Lançamentos relacionados atualizados:', data);
                return atualizarLancamento(lancamentoId, dataRealizado, settledDescription, settledObservation);
            })
            .then(response => response.json())
            .then(data => {
                console.log('Lançamento atualizado com sucesso:', data);
                window.location.reload();
            })
            .catch(error => console.error('Erro:', error));
    } else {
        atualizarLancamento(lancamentoId, dataRealizado, settledDescription, settledObservation)
            .then(response => response.json())
            .then(data => {
                console.log('Lançamento atualizado com sucesso:', data);
                window.location.reload();
            })
            .catch(error => console.error('Erro ao atualizar o lançamento:', error));
    }
  });
});

function atualizarDataLancamentosRelacionados(uuid, novaData) {
  return fetch(`/realizado/atualizar-lancamentos-uuid/${uuid}/`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
      },
      body: JSON.stringify({ novaData: novaData })
  });
}

function atualizarLancamento(lancamentoId, dataRealizado, settledDescription, settledObservation) {
  const dados = { due_date: dataRealizado, description: settledDescription, observation: settledObservation };
  const url = `/realizado/atualizar-lancamento/${lancamentoId}/`;

  fetch(url, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
      },
      body: JSON.stringify(dados)
  })
  .then(response => response.json())
  .then(data => {
      console.log('Lançamento atualizado com sucesso:', data);
      window.location.reload();
  })
  .catch(error => console.error('Erro ao atualizar o lançamento:', error));
}

// Filtro de meses
function selecionarMesAtualEfiltrar() {
  const hoje = new Date();
  let mesAtual = hoje.getMonth(); // 0-11
  let anoAtual = hoje.getFullYear();
  const checkboxes = document.querySelectorAll('#dropdown-content-meses .mes-checkbox');
  const meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

  let checkboxEncontrado = null;

  // Tenta encontrar o checkbox para o mês/ano atual ou para os meses anteriores, se necessário
  while (!checkboxEncontrado && mesAtual >= 0) {
    let mesAnoAtual = `${meses[mesAtual]}/${anoAtual}`;
    checkboxEncontrado = Array.from(checkboxes).find(checkbox => checkbox.value.toLowerCase() === mesAnoAtual.toLowerCase());

    if (!checkboxEncontrado) {
      mesAtual -= 1; // Vai para o mês anterior
      if (mesAtual < 0) {
        // Se chegou a dezembro do ano anterior
        mesAtual = 11; // Mês de dezembro
        anoAtual -= 1; // Ano anterior
      }
    }
  }

  // Se encontrar o checkbox, marca como selecionado e atualiza
  if (checkboxEncontrado) {
    checkboxEncontrado.checked = true;
    updateButtonTextMeses();
    filtrarTabela();
  } else {
    console.error('Nenhum checkbox correspondente ao mês atual ou aos anteriores foi encontrado.');
  }
}

document.addEventListener('DOMContentLoaded', selecionarMesAtualEfiltrar);


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
addListenerAndUpdate('#dropdown-content-contas .conta-checkbox', updateButtonTextContas, filtrarTabela);
addListenerAndUpdate('#dropdown-content-meses .mes-checkbox', updateButtonTextMeses, filtrarTabela);
addListenerAndUpdate('#dropdown-content-bancos .banco-checkbox', updateButtonTextBancos, coletarBancosSelecionados);
addListenerAndUpdate('#dropdown-content-natureza .natureza-checkbox', updateButtonTextNatureza, filtrarTabela);

// Adiciona o listener para click fora do dropdown
document.addEventListener('click', function(event) {
  const dropdowns = [
      {button: "#dropdown-button-contas", content: "dropdown-content-contas"},
      {button: "#dropdown-button-meses", content: "dropdown-content-meses"},
      {button: "#dropdown-button-bancos", content: "dropdown-content-bancos"},
      {button: "#dropdown-button-natureza", content: "dropdown-content-natureza"},
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
      filtrarTabela();
      break;
    case '#dropdown-content-meses':
      updateButtonTextMeses();
      filtrarTabela();
      break;
    case '#dropdown-content-bancos':
      updateButtonTextBancos();
      coletarBancosSelecionados();
      break;
    case '#dropdown-content-natureza':
      updateButtonTextNatureza();
      filtrarTabela();
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

function updateButtonTextContas() {
  updateButtonText('dropdown-button-contas', '#dropdown-content-contas .conta-checkbox', 'Selecione');
}

function updateButtonTextMeses() {
  updateButtonText('dropdown-button-meses', '#dropdown-content-meses .mes-checkbox', 'Selecione');
}

function updateButtonTextBancos() {
  updateButtonText('dropdown-button-bancos', '#dropdown-content-bancos .banco-checkbox', 'Selecione');
}

function updateButtonTextNatureza() {
  const checkboxes = document.querySelectorAll('#dropdown-content-natureza .natureza-checkbox');
  const selectedCheckboxes = document.querySelectorAll('#dropdown-content-natureza .natureza-checkbox:checked');
  const selectedCount = selectedCheckboxes.length;
  const totalOptions = checkboxes.length;
  let buttonText = "Crédito, Débito";
  if (selectedCount > 0 && selectedCount < totalOptions) {
    buttonText = Array.from(selectedCheckboxes).map(cb => cb.nextSibling.textContent.trim()).join(", ");
  }
  document.getElementById('dropdown-button-natureza').textContent = buttonText;
}

let bancosSelecionados = [];
function coletarBancosSelecionados() {
  bancosSelecionados = Array.from(document.querySelectorAll('.banco-checkbox:checked')).map(el => el.value);
  filtrarTabela(); // Filtra a tabela de lançamentos
  // Filtra a tabela de bancos
  document.querySelectorAll('.tabela-bancos .row-bancos').forEach(row => {
    const idBanco = row.getAttribute('data-banco-id');
    row.style.display = bancosSelecionados.length === 0 || bancosSelecionados.includes(idBanco) ? '' : 'none';
  });
  atualizarSaldoTotalBancos(); // Atualiza o saldo total
}

// Filtros
function filtrarTabela() {
  const uuidsGeneralLedgerAccountFilter = Array.from(document.querySelectorAll('#dropdown-content-contas .conta-checkbox:checked')).map(checkbox => checkbox.value);
  const intervalosMesesSelecionados = Array.from(document.querySelectorAll('#dropdown-content-meses .mes-checkbox:checked')).map(checkbox => ({
    inicio: new Date(checkbox.getAttribute('data-inicio-mes')),
    fim: new Date(checkbox.getAttribute('data-fim-mes'))
  }));
  const naturezasSelecionadas = Array.from(document.querySelectorAll('#dropdown-content-natureza .natureza-checkbox:checked'), cb => cb.value);

  // Verificações de seleção total ou nenhuma seleção simplificadas
  const selecionarTodosMeses = intervalosMesesSelecionados.length === 0;
  const selecionarTodaNatureza = naturezasSelecionadas.length === 0;
  
  // Obtenção dos filtros de texto e datas
  const descriptionFilter = document.getElementById("caixa-pesquisa").value.toUpperCase();
  const filtroTags = document.getElementById("caixa-pesquisa-tags").value.toUpperCase();
  const dataInicioObj = document.getElementById("data-inicio").value ? new Date(document.getElementById("data-inicio").value) : null;
  const dataFimObj = document.getElementById("data-fim").value ? new Date(document.getElementById("data-fim").value) : null;
  let mesesAnosVisiveis = new Set();

  document.querySelectorAll('.row-lancamentos').forEach(function(row) {
    const uuidGeneralLedgerAccount = row.getAttribute('data-uuid-general-ledger-account');
    const description = row.querySelector(".description-row").textContent.toUpperCase();
    const observationElement = row.querySelector(".observation-row").cloneNode(true);
    const tagsElemento = observationElement.querySelector(".d-block");
    if (tagsElemento) observationElement.removeChild(tagsElemento);
    const observation = observationElement.textContent.toUpperCase();
    const tags = tagsElemento ? tagsElemento.textContent.toUpperCase() : "";
    const dueDate = new Date(row.querySelector(".due_date-row").textContent.split('/').reverse().join('-'));
    const naturezaLancamento = row.getAttribute('data-natureza');
    const idBancoLancamento = row.getAttribute('data-banco-id-liquidacao');

    
    const generalLedgerAccountMatch = uuidsGeneralLedgerAccountFilter.length === 0 || uuidsGeneralLedgerAccountFilter.includes(uuidGeneralLedgerAccount);
    const descriptionObservationMatch = descriptionFilter === "" || description.includes(descriptionFilter) || observation.includes(descriptionFilter);
    const tagMatch = filtroTags === "" || tags.includes(filtroTags);
    const mesMatch = selecionarTodosMeses || intervalosMesesSelecionados.some(intervalo => dueDate >= intervalo.inicio && dueDate <= intervalo.fim);
    const dataMatch = (!dataInicioObj || dueDate >= dataInicioObj) && (!dataFimObj || dueDate <= dataFimObj);
    const naturezaMatch = selecionarTodaNatureza || naturezasSelecionadas.includes(naturezaLancamento);
    const bancoMatch = bancosSelecionados.length === 0 || bancosSelecionados.includes(idBancoLancamento);

    row.style.display = descriptionObservationMatch && tagMatch && mesMatch && naturezaMatch && dataMatch && generalLedgerAccountMatch && bancoMatch ? "" : "none";

    if (row.style.display === "") {
      let mesAno = dueDate.toLocaleString('default', { month: '2-digit', year: 'numeric' });
      mesesAnosVisiveis.add(mesAno);
    }
  });

  // Simplificação na filtragem das linhas de total do mês
  document.querySelectorAll("#tabela-lancamentos .linha-total-mes").forEach(row => {
    let textoMesAno = row.querySelector("td:nth-child(2)").textContent;
    let mesAnoMatch = textoMesAno.match(/\d{2}\/\d{4}$/); // Captura MM/YYYY
    row.style.display = mesAnoMatch && mesesAnosVisiveis.has(mesAnoMatch[0]) ? "" : "none";
  });

  atualizarSaldoTotalBancos();
}

document.getElementById('caixa-pesquisa').addEventListener('input', filtrarTabela);
document.getElementById('caixa-pesquisa-tags').addEventListener('input', filtrarTabela);
document.getElementById('data-inicio').addEventListener('change', filtrarTabela);
document.getElementById('data-fim').addEventListener('change', filtrarTabela);

// Inicializa listeners de mudança para os checkboxes dos bancos
document.querySelectorAll('.banco-checkbox').forEach(checkbox => {
  checkbox.addEventListener('change', coletarBancosSelecionados);
});

// 5. Saldo total dos bancos
function atualizarSaldoTotalBancos() {
  let newTotalBalance = 0;
  const linhasBancos = document.querySelectorAll('.tabela-bancos .row-bancos');

  linhasBancos.forEach(row => {
    const idBanco = row.getAttribute('data-banco-id');
    if (bancosSelecionados.length === 0 || bancosSelecionados.includes(idBanco)) {
      let strAmount = row.querySelector('.saldo-banco-row').textContent;
      strAmount = strAmount.replace('R$', '').replace(/\./g, '').replace(',', '.').trim();
      const balance = parseFloat(strAmount);
      newTotalBalance += balance;
    }
  });

  // Atualiza o saldo total global e na interface
  saldoTotal = newTotalBalance;
  const saldoTotalFormatado = saldoTotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  document.querySelector('.saldo-total-banco-row').textContent = saldoTotalFormatado;

  // Chama a função para atualizar os saldos das linhas com o novo saldo total
  atualizarSaldosDasLinhas();
}

// Função para atualizar os saldos de cada linha na tabela de lançamentos
function atualizarSaldosDasLinhas() {
  let saldoAtual = saldoTotal;

  // Obtém todas as linhas de lançamento e as converte para um array
  const linhas = Array.from(document.querySelectorAll('.row-lancamentos'));

  // Itera sobre as linhas de lançamento de baixo para cima
  for (let i = linhas.length - 1; i >= 0; i--) {
    const row = linhas[i];
    const idBancoLancamento = row.getAttribute('data-banco-id-liquidacao');

    // Se um único banco está selecionado e esta linha não pertence a ele, pular para a próxima
    if (bancosSelecionados.length === 1 && bancosSelecionados[0] !== idBancoLancamento) {
      continue;
    }

    // Obter a natureza da linha e ajustar o saldo
    const natureza = row.getAttribute('data-natureza').trim();
    let amount = 0;

    if (natureza === 'Crédito') {
      const creditAmount = row.querySelector('.credito-row').textContent;
      amount = parseFloat(creditAmount.replace('R$', '').replace(/\./g, '').replace(',', '.').trim());
      saldoAtual -= amount; // Crédito subtrai do saldo
    } else if (natureza === 'Débito') {
      const debitAmount = row.querySelector('.debito-row').textContent;
      amount = parseFloat(debitAmount.replace('R$', '').replace(/\./g, '').replace(',', '.').trim());
      saldoAtual += amount; // Débito soma ao saldo
    }
    
    // Atualizar o saldo da linha
    row.querySelector('.saldo-row').textContent = saldoAtual.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
}

// Adicionar event listeners para atualizar o saldo quando a seleção de bancos mudar
document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll('.banco-checkbox').forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      coletarBancosSelecionados();
      atualizarSaldoTotalBancos(); // Isso irá recalcular o saldo total e atualizar as linhas de lançamento
    });
  });

  // Chamada inicial para configurar o saldo
  coletarBancosSelecionados();
  atualizarSaldoTotalBancos();
});

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