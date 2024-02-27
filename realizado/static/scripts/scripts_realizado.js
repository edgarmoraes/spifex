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
            vencimento: row.querySelector('.vencimento-row').textContent,
            descricao: row.querySelector('.descricao-row').textContent,
            valor: debito || credito, // Usa débito se disponível, senão credito
            conta_contabil: row.getAttribute('data-conta-contabil'),
            parcela_atual: row.getAttribute('parcela-atual'),
            parcelas_total: row.getAttribute('parcelas-total'),
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
      row.addEventListener('dblclick', function() {
          abrirModalEdicao(this);
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
  const vencimento = row.querySelector('.vencimento-row').textContent.trim();
  const descricao = row.querySelector('.descricao-row').textContent.trim();
  const observacao = row.querySelector('.obs-row').textContent.split('Tags:')[0].trim().replace(/\s+/g, ' ');
  const valor = row.querySelector('.debito-row').textContent.trim() || row.querySelector('.credito-row').textContent.trim();
  const contaContabil = row.getAttribute('data-conta-contabil');
  const tags = row.querySelector('.obs-row').textContent.trim().split('Tags:')[1];
  const parcelaAtual = row.getAttribute('parcela-atual');
  const parcelasTotal = row.getAttribute('parcelas-total');
  const uuid = row.getAttribute('data-uuid-correlacao');
  const uuidParcelas = row.getAttribute('data-uuid-correlacao-parcelas');

  preencherDadosModalRealizado(id, vencimento, descricao, observacao, valor, contaContabil, tags, parcelaAtual, parcelasTotal, uuid, uuidParcelas);

  document.getElementById('modal-realizado').showModal();
  document.body.style.overflow = 'hidden';
  document.body.style.marginRight = '17px';
  document.querySelector('.nav-bar').style.marginRight = '17px';
}

function preencherDadosModalRealizado(id, vencimento, descricao, observacao, valor, contaContabil, tags, parcelaAtual, parcelasTotal, uuid, uuidParcelas) {
  document.querySelector('.modal-form-realizado [name="lancamento_id_realizado"]').value = id;
  document.getElementById('data-realizado').value = formatarDataParaInput(vencimento);
  document.getElementById('descricao-realizado').value = descricao;
  document.getElementById('observacao-realizado').value = observacao;
  document.getElementById('valor-realizado').value = "R$ "+valor;
  document.getElementById('conta-contabil-realizado').value = contaContabil;
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
  modal.close();
  document.body.style.overflow = '';
  document.body.style.marginRight = '';
  document.querySelector('.nav-bar').style.marginRight = '';
  const form = document.querySelector(".modal-form-realizado");
  form.reset();
  document.getElementById('tag-container-realizado').innerHTML = ''; // Limpa as tags
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
      const descricaoRealizado = document.getElementById('descricao-realizado').value;
      const observacaoRealizado = document.getElementById('observacao-realizado').value;
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
                return atualizarLancamento(lancamentoId, dataRealizado, descricaoRealizado, observacaoRealizado);
            })
            .then(response => response.json())
            .then(data => {
                console.log('Lançamento atualizado com sucesso:', data);
                window.location.reload();
            })
            .catch(error => console.error('Erro:', error));
    } else {
        atualizarLancamento(lancamentoId, dataRealizado, descricaoRealizado, observacaoRealizado)
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

function atualizarLancamento(lancamentoId, dataRealizado, descricaoRealizado, observacaoRealizado) {
  const dados = { vencimento: dataRealizado, descricao: descricaoRealizado, observacao: observacaoRealizado };
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


















// 1. Definições de Funções Básicas
function toggleDropdownMeses(event) {
  event.stopPropagation();
  document.getElementById("dropdown-content-meses").classList.toggle("show");
}

function updateButtonTextMeses() {
  const totalMeses = document.querySelectorAll('#dropdown-content-meses .mes-checkbox').length;
  const totalSelecionados = document.querySelectorAll('#dropdown-content-meses .mes-checkbox:checked').length;
  const buttonText = document.getElementById('dropdown-button-meses');
  buttonText.textContent = totalSelecionados === 0 ? 'Selecione' : 
                           totalSelecionados === totalMeses ? 'Todos Selecionados' : 
                           `${totalSelecionados} Selecionado(s)`;
}

function selectAllMeses(event) {
  event.stopPropagation();
  document.querySelectorAll('#dropdown-content-meses .mes-checkbox').forEach(checkbox => checkbox.checked = true);
  updateButtonTextMeses();
  filtrarTabela();
}

function deselectAllMeses(event) {
  event.stopPropagation();
  document.querySelectorAll('#dropdown-content-meses .mes-checkbox').forEach(checkbox => checkbox.checked = false);
  updateButtonTextMeses();
  filtrarTabela();
}

// 2. Lógica de Seleção de Mês
function selecionarMesAtualEfiltrar() {
  const today = new Date();
  let month = today.getMonth(); // Mês atual como número (0-11)
  const year = today.getFullYear();

  const checkboxes = document.querySelectorAll('#dropdown-content-meses .mes-checkbox');
  const meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  let found = false;

  while (!found && month >= 0) {
      const currentMonthYear = `${meses[month]}/${year}`;
      checkboxes.forEach(checkbox => {
          if (checkbox.value.toLowerCase() === currentMonthYear) {
              checkbox.checked = true;
              found = true;
          }
      });
      if (!found) {
          month--;
          if (month < 0) {
              month = 11;
              year--;
          }
      }
  }
  if (!found) {
      console.error('Nenhum checkbox correspondente aos meses anteriores encontrado.');
  }
  updateButtonTextMeses();
  filtrarTabela();
}

function formatarDataParaMesAno(data) {
  const meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
  const partesData = data.split('/');
  const mes = parseInt(partesData[1], 10) - 1; // Converte 'mm' para índice de array (0-11)
  const ano = partesData[2]; // 'aaaa'
  return `${meses[mes]}/${ano}`; // Retorna 'mmm/aaaa'
}

// 3. Inicialização e Event Listeners
document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll('#dropdown-content-meses .mes-checkbox').forEach(checkbox => {
      checkbox.addEventListener('change', () => {
          updateButtonTextMeses();
          filtrarTabela();
      });
  });

  document.addEventListener('click', event => {
      if (!event.target.closest("#dropdown-content-meses") && !event.target.closest("#dropdown-button-meses")) {
          document.getElementById("dropdown-content-meses").classList.remove("show");
      }
  });

  selecionarMesAtualEfiltrar();
});

// 4. Filtragem da Tabela
function filtrarTabela() {
  const contaContabilSelecionada = document.getElementById('contas-contabeis').value;
  const dataInicio = document.getElementById('data-inicio').value;
  const dataFim = document.getElementById('data-fim').value;
  const naturezaSelecionada = document.getElementById('natureza').value;
  const mesesSelecionados = Array.from(document.querySelectorAll('.mes-checkbox:checked')).map(el => el.value);
  const inputDescricao = document.getElementById('caixa-pesquisa').value.toLowerCase();
  const inputTags = document.getElementById('caixa-pesquisa-tags').value.toLowerCase();

  document.querySelectorAll('.row-lancamentos').forEach(function(row) {
      const contaContabil = row.getAttribute('data-conta-contabil');
      const data = row.querySelector('.vencimento-row').textContent;
      const natureza = row.querySelector('.natureza-row') !== null ? naturezaSelecionada : "";
      const descricao = row.querySelector('.descricao-row').textContent.toLowerCase();
      const observacao = row.querySelector('.obs-row').textContent.toLowerCase();
      const tags = row.querySelector('.d-block').textContent.toLowerCase();
      const mesAno = formatarDataParaMesAno(data); // Função para converter data para 'mmm/aaaa'

      const descricaoMatch = descricao.includes(inputDescricao);
      const observacaoMatch = observacao.includes(inputDescricao) && !tags.includes(inputDescricao);
      const tagsMatch = tags.includes(inputTags);

      const contaContabilMatch = contaContabilSelecionada === "" || contaContabil === contaContabilSelecionada;
      const dataMatch = !dataInicio || !dataFim || (data >= dataInicio && data <= dataFim);
      const naturezaMatch = naturezaSelecionada === "" || natureza === naturezaSelecionada.toLowerCase();
      const mesMatch = mesesSelecionados.length === 0 || mesesSelecionados.includes(mesAno);

      if (contaContabilMatch && dataMatch && naturezaMatch && mesMatch && (descricaoMatch || observacaoMatch) && tagsMatch) {
          row.style.display = "";
      } else {
          row.style.display = "none";
      }
  });
}

// Eventos adicionais para filtragem e interações
document.getElementById('caixa-pesquisa').addEventListener('input', filtrarTabela);
document.getElementById('caixa-pesquisa-tags').addEventListener('input', filtrarTabela);
document.getElementById('contas-contabeis').addEventListener('change', filtrarTabela);
document.getElementById('data-inicio').addEventListener('change', filtrarTabela);
document.getElementById('data-fim').addEventListener('change', filtrarTabela);
document.getElementById('natureza').addEventListener('change', filtrarTabela);
document.querySelectorAll('.mes-checkbox').forEach(checkbox => {
  checkbox.addEventListener('change', filtrarTabela);
});