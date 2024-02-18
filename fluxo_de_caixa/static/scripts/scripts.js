// Evitar bancos iguais no processo de transferência
document.addEventListener("DOMContentLoaded", function() {
  const formularioTransferencia = document.querySelector(".modal-form-transferencias");

  formularioTransferencia.addEventListener("submit", function(e) {
      const bancoSaidaId = document.getElementById("banco-saida").value;
      const bancoEntradaId = document.getElementById("banco-entrada").value;

      if (bancoSaidaId === bancoEntradaId) {
          e.preventDefault(); // Impede o envio do formulário
          alert("O banco de saída não pode ser igual ao banco de entrada. Por favor, selecione bancos diferentes.");
      }
  });
});

// Função para formatar o valor de texto para número
function formatarValor(valorTexto) {
  // Remove pontos e substitui vírgula por ponto para conversão para número
  // Garante que o valorTexto é uma string antes de fazer as substituições
  valorTexto = valorTexto.toString();
  var valorNumerico = valorTexto.replace(/\./g, '').replace(',', '.');
  return parseFloat(valorNumerico);
}

// Função para atualizar o saldo do banco selecionado
function atualizarSaldoBanco() {
  // Inicializar o valor total a liquidar
  let valorTotalLiquidar = 0;
  
  // Obter o valor total a liquidar dos lançamentos selecionados
  document.querySelectorAll('.row-lancamentos').forEach(row => {
    const checkbox = row.querySelector('.checkbox-personalizado');
    if (checkbox && checkbox.checked) {
      const credito = row.querySelector('.credito-row').textContent.trim();
      const debito = row.querySelector('.debito-row').textContent.trim();

      if (credito) {
        valorTotalLiquidar += formatarValor(credito);
      }
      if (debito) {
        valorTotalLiquidar -= formatarValor(debito);
      }
    }
  });

  // Iterar por todos os checkboxes dos bancos
  document.querySelectorAll('.checkbox-personalizado-liquidacao').forEach(checkbox => {
    if (checkbox.checked) {
      // Encontrar o elemento de saldo inicial do banco correspondente
      let saldoInicialEl = checkbox.closest('.row-bancos').querySelector('[name="saldo_inicial"]');
      let saldoInicial = formatarValor(saldoInicialEl.textContent);
      
      // Calcular o novo saldo
      let novoSaldo = saldoInicial + valorTotalLiquidar;

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
      // Manipula a visibilidade da seção 'valor-parcial-liquidacao' com base no estado do checkbox
      const lancamentoSelecionado = event.target.closest('.lancamentos-selecionados');
      const secaoValorParcial = lancamentoSelecionado.querySelector('.valor-parcial-liquidacao');
      secaoValorParcial.style.display = event.target.checked ? 'block' : 'none';
      
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
  configurarEstadoInicialValor(div, lancamentoDados.id);
}

function extrairDadosLancamento(checkbox) {
  const row = checkbox.closest('.row-lancamentos');
  const id = checkbox.getAttribute('data-id');
  return {
      id: id,
      descricao: row.querySelector('.descricao-row').textContent,
      vencimento: row.querySelector('.vencimento-row').textContent,
      observacao: extrairObservacao(row),
      valor: extrairValor(row),
      natureza: extrairNatureza(row)
  };
}

function extrairObservacao(row) {
  let observacao = row.querySelector('.obs-row').textContent.trim();
  return observacao.split('Tags:')[0].trim();
}

function extrairValor(row) {
  const valorDebito = row.querySelector('.debito-row').textContent;
  const valorCredito = row.querySelector('.credito-row').textContent;
  return valorDebito || valorCredito;
}

function extrairNatureza(row) {
  return row.querySelector('.debito-row').textContent ? "Débito" : "Crédito";
}

function montarDivLancamento({id, descricao, vencimento, observacao, valor, natureza}) {
  const div = document.createElement('div');
  div.classList.add('lancamentos-selecionados');
  div.innerHTML = `
    <section class="modal-flex data-liquidacao">
        <input class="modal-data data-liquidacao" id="data-liquidacao-${id}" type="date" name="data-liquidacao-${id}" value="${formatarDataParaInput(vencimento)}" required>
    </section>
    <section class="modal-flex">
        <input class="modal-descricao" id="descricao-liquidacao-${id}" maxlength="100" type="text" name="descricao-liquidacao-${id}" value="${descricao}" readonly style="background-color: #ababab; color: #ffffff;">
    </section>
    <section class="modal-flex">
        <input class="modal-obs" id="observacao-liquidacao-${id}" maxlength="100" type="text" name="observacao-liquidacao-${id}" value="${observacao}">
    </section>
    <section class="modal-flex">
        <input class="modal-valor valor-liquidacao-total" id="valor-liquidacao-${id}" type="text" name="valor-liquidacao-${id}" oninput="formatarCampoValor(this)" value="${formatarValorDecimal(valor)}" readonly required style="background-color: #ababab; color: #ffffff;">
    </section>
    <section class="modal-flex natureza-liquidacao">
        <input class="modal-natureza" id="natureza-liquidacao-${id}" type="text" name="natureza-liquidacao-${id}" value="${natureza}" readonly style="background-color: #ababab; color: #ffffff;">
    </section>
    <section class="modal-botao-parcial">
      <div>
      <label class="form-switch"><input id="botao-parcial-${id}" class="botao-parcial" type="checkbox"><i></i></label>
      </div>
    </section>
    <section class="modal-flex valor-parcial-liquidacao" style="display:none;">
    <input class="modal-valor valor-parcial" id="valor-parcial-liquidacao-${id}" type="text" name="valor-parcial-liquidacao-${id}" oninput="formatarCampoValor(this)" value="" required>
    </section>
    `;
  return div;
}
  
function configurarEstadoInicialValor(div, id) {
    const botaoParcial = div.querySelector('.botao-parcial');
    botaoParcial.addEventListener('change', function() {
        const campoValorParcial = div.querySelector('.valor-parcial-liquidacao');
        campoValorParcial.style.display = botaoParcial.checked ? 'block' : 'none';
    });
}

function formatarDataParaInput(data) {
    const partes = data.split('/');
    return `${partes[2]}-${partes[1]}-${partes[0]}`;
}

function formatarValorDecimal(valor) {
    valor = valor.replace(/\./g, '').replace(',', '.');
    const numero = parseFloat(valor);
    return !isNaN(numero) ? numero.toFixed(2) : '0.00';
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
    let campoValorParcial = document.getElementById(`valor-parcial-liquidacao-${id}`);
    let valorParcial = campoValorParcial && campoValorParcial.value ? parseFloat(campoValorParcial.value.replace(/\D/g, '').replace(',', '.')) : 0;

    if (botaoParcial.checked && (valorParcial <= 0 || isNaN(valorParcial))) {
      alert('Por favor, preencha o valor parcial para realizar uma liquidação parcial.');
      campoValorParcial.focus();
      return;
    }
    
    let campoValorTotal = document.getElementById(`valor-liquidacao-${id}`);
    let valorTotal = parseFloat(campoValorTotal.value.replace(/\D/g, '').replace(',', '.'));
    if (valorParcial > valorTotal) {
      alert('O valor parcial não pode ser maior que o valor total da liquidação.');
      campoValorParcial.focus();
      return;
    }
    
    let campoObservacao = document.getElementById(`observacao-liquidacao-${id}`);


    let itemData = {
      id: id,
      vencimento: row.querySelector('.vencimento-row').textContent,
      descricao: row.querySelector('.descricao-row').textContent,
      observacao: campoObservacao ? campoObservacao.value : '',
      valor: campoValorTotal.value,
      conta_contabil: row.getAttribute('data-conta-contabil'),
      parcela_atual: row.getAttribute('parcela-atual'),
      parcelas_total: row.getAttribute('parcelas-total'),
      natureza: row.querySelector('.debito-row').textContent ? 'Débito' : 'Crédito',
      data_liquidacao: campoData ? campoData.value : '',
      banco_liquidacao: nomeBancoSelecionado,
      banco_id_liquidacao: idBancoSelecionado,
      valor_parcial: valorParcial > 0 ? campoValorParcial.value : undefined,
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


// Seleciona o botão pelo ID
const botaoTeste = document.getElementById('liquidar-button');

// Seleciona o modal pelo ID
const modalLiquidacao = document.getElementById('modal-liquidacoes');

// Adiciona um ouvinte de eventos ao botão para abrir o modal
botaoTeste.addEventListener('click', function() {
    modalLiquidacao.showModal(); // Abre o modal
});

// Opcional: Adiciona um ouvinte de eventos para fechar o modal no botão de cancelar, se houver
const botaoFechar = modalLiquidacao.querySelector('.modal-fechar-liquidacoes');
if (botaoFechar) {
    botaoFechar.addEventListener('click', function() {
        modalLiquidacao.close(); // Fecha o modal
    });
}


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
function abrirModal(openBtn, modal) {
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

  // Verifica se o tagContainer existe antes de tentar manipulá-lo
  const tagContainer = document.getElementById(tagContainerId);
  if (tagContainer) {
      while (tagContainer.firstChild) {
          tagContainer.removeChild(tagContainer.firstChild);
      }
  }

  // Verifica se o tagInput existe antes de tentar manipulá-lo
  const tagInput = document.getElementById(tagInputId);
  if (tagInput) {
      tagInput.value = '';
  }

  // Verifica se o tagsHiddenInput existe antes de tentar manipulá-lo
  const tagsHiddenInput = document.getElementById(tagsHiddenInputId);
  if (tagsHiddenInput) {
      tagsHiddenInput.value = '';
  }

  // Verifica se o parcelasInput existe antes de tentar manipulá-lo
  const parcelasInput = document.getElementById(parcelasId);
  if (parcelasInput) {
      parcelasInput.value = '1'; // Define o valor padrão para 1
      parcelasInput.style.display = 'none'; // Oculta o campo de parcelas
      parcelasInput.disabled = false; // Habilita o campo de parcelas
  }

    // Oculta as seções de liquidação parcial e remove a classe 'ativo' dos elementos ajustáveis
    const secoesValorParcial = document.querySelectorAll('.valor-parcial-liquidacao');
    secoesValorParcial.forEach(secao => {
      secao.style.display = 'none';
    });
  
    const elementosParaAjustar = document.querySelectorAll('.lancamentos-selecionados, .label-lancamentos-selecionados');
    elementosParaAjustar.forEach(el => {
      el.classList.remove('ativo');
    });
  
    const labelParcial = document.querySelector('.label-parcial');
    if (labelParcial) labelParcial.style.display = 'none';
  
    // Desmarca todos os checkboxes 'botao-parcial'
    const todosBotoesParcial = document.querySelectorAll('.botao-parcial');
    todosBotoesParcial.forEach(checkbox => {
      checkbox.checked = false;
    });
  
    // Atualiza o estado das colunas para refletir a remoção da classe 'ativo'
    atualizarEstadoColunas();
}


// Elementos do DOM
const openModalRecebimentos = document.querySelector('.recebimentos');
const openModalPagamentos = document.querySelector('.pagamentos');
const openModalTransferencias = document.querySelector('.transferencias');
const openModalLiquidacoes = document.querySelector('.liquidar-button');

const closeModalRecebimentos = document.querySelector('.modal-fechar-recebimentos');
const closeModalPagamentos = document.querySelector('.modal-fechar-pagamentos');
const closeModalTransferencias = document.querySelector('.modal-fechar-transferencias');
const closeModalLiquidacoes = document.querySelector('.modal-fechar-liquidacoes');

const modalRecebimentos = document.querySelector('.modal-recebimentos');
const modalPagamentos = document.querySelector('.modal-pagamentos');
const modalTransferencias = document.querySelector('.modal-transferencias');
const modalLiquidacoes = document.querySelector('.modal-liquidacoes');

// Event Listeners
abrirModal(openModalRecebimentos, modalRecebimentos, ".modal-form-recebimentos", 'tagInput-recebimentos', 'tagsHiddenInput-recebimentos', 'tag-container-recebimentos');
fecharModal(closeModalRecebimentos, modalRecebimentos, ".modal-form-recebimentos", 'tagInput-recebimentos', 'tagsHiddenInput-recebimentos', 'tag-container-recebimentos', "parcelas-section-recebimentos");

abrirModal(openModalPagamentos, modalPagamentos, ".modal-form-pagamentos", 'tagInput-pagamentos', 'tagsHiddenInput-pagamentos', 'tag-container-pagamentos');
fecharModal(closeModalPagamentos, modalPagamentos, ".modal-form-pagamentos", 'tagInput-pagamentos', 'tagsHiddenInput-pagamentos', 'tag-container-pagamentos', "parcelas-section-pagamentos");

abrirModal(openModalTransferencias, modalTransferencias, ".modal-form-transferencias");
fecharModal(closeModalTransferencias, modalTransferencias, ".modal-form-transferencias");

abrirModal(openModalLiquidacoes, modalLiquidacoes, ".modal-form-liquidacoes");
fecharModal(closeModalLiquidacoes, modalLiquidacoes, ".modal-form-liquidacoes");


// Evento para editar lançamentos ao clicar duas vezes nas células da tabela
// Variáveis Globais
let estaEditando = false;

// Event Listeners Principais
document.addEventListener('DOMContentLoaded', function() {
    configurarEventosModais();
    configurarEventosTabela();
});

function configurarEventosModais() {
    // Fechar modais ao pressionar a tecla Escape
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            fecharModais();
        }
    });

    // Configuração do fechamento do modal
    document.getElementById('modal-recebimentos').onclose = function() {
        onModalClose('recebimentos');
    };
    document.getElementById('modal-pagamentos').onclose = function() {
        onModalClose('pagamentos');
    };
}

function configurarEventosTabela() {
    // Evento para editar lançamentos ao clicar duas vezes nas células da tabela
    document.querySelectorAll('.row-lancamentos td:not(.checkbox-row)').forEach(cell => {
        cell.addEventListener('dblclick', function() {
            handleCellDoubleClick(cell);
        });
    });
}

// Funções de Manipulação de Modais
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
        var form = document.querySelector(".modal-form-recebimentos"); // Adapte o seletor conforme necessário
        form.reset(); // Reseta o formulário
        document.getElementById('modal-recebimentos').close();
    }
    if (document.getElementById('modal-pagamentos').open) {
        var form = document.querySelector(".modal-form-pagamentos"); // Adapte o seletor conforme necessário
        form.reset(); // Reseta o formulário
        document.getElementById('modal-pagamentos').close();
    }
}

function abrirModalRecebimentosEdicao(row) {
    estaEditando = true;
    preencherDadosModal(row, 'recebimentos');
    mostrarParcelasRecebimentos(row);
    document.getElementById('modal-recebimentos').showModal();
    document.body.style.overflow = 'hidden';
    document.body.style.marginRight = '17px';
    document.querySelector('.nav-bar').style.marginRight = '17px';
}

function abrirModalPagamentosEdicao(row) {
    estaEditando = true;
    preencherDadosModal(row, 'pagamentos');
    mostrarParcelasPagamentos(row);
    document.getElementById('modal-pagamentos').showModal();
    document.body.style.overflow = 'hidden';
    document.body.style.marginRight = '17px';
    document.querySelector('.nav-bar').style.marginRight = '17px';
}

function onModalClose(tipo) {
    estaEditando = false;
    limparCamposModal(tipo);
    redefinirCampoParcelas(tipo);
}

// Funções Auxiliares de Modais
function preencherDadosModal(row, tipo) {
    const parcelasTotalOriginais = row.getAttribute('parcelas-total');
    document.getElementById(`parcelas-total-originais-${tipo}`).value = parcelasTotalOriginais;

    const vencimento = row.querySelector('.vencimento-row').textContent.trim();
    document.getElementById(`data-${tipo}`).value = formatarDataParaInput(vencimento);

    const valor = row.querySelector(`.${tipo === 'recebimentos' ? 'credito' : 'debito'}-row`).textContent.trim();
    document.getElementById(`valor-${tipo}`).value = desformatarNumero(valor);

    document.getElementById(`descricao-${tipo}`).value = row.querySelector('.descricao-row').textContent.trim();
    document.getElementById(`observacao-${tipo}`).value = row.querySelector('.obs-row').childNodes[0].textContent.trim();

    const tags = extrairTags(row);
    document.getElementById(`tagInput-${tipo}`).value = tags;

    document.getElementById(`conta-contabil-${tipo}`).value = row.dataset.contaContabil;

    const lancamentoId = row.querySelector('.checkbox-personalizado').getAttribute('data-id');
    document.querySelector(`[name="lancamento_id_${tipo}"]`).value = lancamentoId;

    const uuid = row.querySelector('.checkbox-personalizado').getAttribute('data-uuid-row');
    document.querySelector(`[name="uuid_${tipo}"]`).value = uuid;

      // Bloqueia a edição do campo 'valor' caso o 'data-uuid-row' seja diferente de 'none'
    if (uuid !== 'None') {
      var element = document.getElementById(`valor-${tipo}`);
      element.readOnly = true;
      element.style.backgroundColor = '#B5B5B5';
      element.style.color = '#FFFFFF';
    } else {
        document.getElementById(`valor-${tipo}`).readOnly = false;
    }

    simularEnter(`tagInput-${tipo}`);
}

function limparCamposModal(tipo) {
    const inputs = document.querySelectorAll(`.modal-form-${tipo} input`);
    inputs.forEach(input => {
        if (input.type !== 'submit' && input.name !== 'csrfmiddlewaretoken') {
            input.value = '';
        }
    });
}

function redefinirCampoParcelas(tipo) {
    var select = document.getElementById(`recorrencia-${tipo}`);
    var input = document.getElementById(`parcelas-${tipo}`);
    var section = document.getElementById(`parcelas-section-${tipo}`);

    section.style.display = select.value === 'sim' ? 'block' : 'none';
    input.value = select.value === 'sim' ? '' : '1';
    input.disabled = false;
}

// Função para mostrar campo de recorrência
function mostrarParcelasRecebimentos(row) {
  var select = document.getElementById('recorrencia-recebimentos');
  var section = document.getElementById('parcelas-section-recebimentos');
  var input = document.getElementById('parcelas-recebimentos');

  section.style.display = select.value === 'sim' ? 'block' : 'none';
  if (estaEditando) {
      var parcelasTotal = row.getAttribute('parcelas-total') ? parseInt(row.getAttribute('parcelas-total')) : 1;
      var parcelaAtual = row.getAttribute('parcela-atual') ? parseInt(row.getAttribute('parcela-atual')) : 1;

      input.value = parcelaAtual;
      input.disabled = parcelasTotal > 1;
  } else {
      input.value = select.value === 'sim' ? '' : '1';
      input.disabled = false;
  }
}

function mostrarParcelasPagamentos(row) {
  var select = document.getElementById('recorrencia-pagamentos');
  var section = document.getElementById('parcelas-section-pagamentos');
  var input = document.getElementById('parcelas-pagamentos');

  section.style.display = select.value === 'sim' ? 'block' : 'none';
  if (estaEditando) {
      var parcelasTotal = row.getAttribute('parcelas-total') ? parseInt(row.getAttribute('parcelas-total')) : 1;
      var parcelaAtual = row.getAttribute('parcela-atual') ? parseInt(row.getAttribute('parcela-atual')) : 1;

      input.value = parcelaAtual;
      input.disabled = parcelasTotal > 1;
  } else {
      input.value = select.value === 'sim' ? '' : '1';
      input.disabled = false;
  }
}

// Funções de Eventos de Tabela
function handleCellDoubleClick(cell) {
  const row = cell.closest('.row-lancamentos');
  abrirModalEdicao(row);
}

// Funções de Formatação e Utilidades
function desformatarNumero(valorFormatado) {
  return valorFormatado.replace(/\./g, '').replace(',', '.');
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


// Função para formatar o valor de um campo como moeda brasileira
function formatarCampoValor(input) {
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

// Filtros
function filtrarTabela() {
  var selectMeses = document.getElementById("meses");
  var optionSelecionada = selectMeses.options[selectMeses.selectedIndex];
  var inicioMesDate = optionSelecionada.getAttribute('data-inicio-mes') ? new Date(optionSelecionada.getAttribute('data-inicio-mes')) : null;
  var fimMesDate = optionSelecionada.getAttribute('data-fim-mes') ? new Date(optionSelecionada.getAttribute('data-fim-mes')) : null;

  var dataInicio = document.getElementById("data-inicio").value;
  var dataFim = document.getElementById("data-fim").value;
  var filtroDescricao = document.getElementById("caixa-pesquisa").value.toUpperCase();
  var filtroTags = document.getElementById("caixa-pesquisa-tags").value.toUpperCase();
  var filtroContaContabil = document.getElementById("contas-contabeis").value.toUpperCase();
  var filtroNatureza = document.getElementById("natureza").value;

  var tabela = document.getElementById("tabela-lancamentos");
  var tr = tabela.getElementsByTagName("tr");

  var dataInicioObj = dataInicio ? new Date(dataInicio) : null;
  var dataFimObj = dataFim ? new Date(dataFim) : null;

  for (var i = 0; i < tr.length; i++) {
      var tdDescricao = tr[i].getElementsByClassName("descricao-row")[0];
      var tdObservacao = tr[i].getElementsByClassName("obs-row")[0];
      var contaContabil = tr[i].getAttribute('data-conta-contabil').toUpperCase();
      var tdVencimento = tr[i].getElementsByClassName("vencimento-row")[0];
      var dataVencimento = new Date(tdVencimento.textContent.split('/').reverse().join('-'));
      var tdTags = tr[i].getElementsByClassName("d-block")[0];

      var txtDescricao = tdDescricao ? tdDescricao.textContent || tdDescricao.innerText : "";
      var txtObservacao = tdObservacao ? tdObservacao.textContent.split("Tags:")[0].trim() : "";
      var naturezaLancamento = tr[i].querySelector(".credito-row").textContent.trim() ? 'credito' : 'debito';
      var txtTags = tdTags ? tdTags.textContent.toUpperCase() : "";

      var descricaoObservacaoMatch = txtDescricao.toUpperCase().indexOf(filtroDescricao) > -1 || txtObservacao.toUpperCase().indexOf(filtroDescricao) > -1;
      var tagMatch = filtroTags === "" || txtTags.indexOf(filtroTags) > -1;
      var contaContabilMatch = filtroContaContabil === "" || contaContabil.toUpperCase().indexOf(filtroContaContabil) > -1;
      var mesMatch = (!inicioMesDate && !fimMesDate) || (dataVencimento >= inicioMesDate && dataVencimento <= fimMesDate);
      var naturezaMatch = filtroNatureza === "" || filtroNatureza === naturezaLancamento;
      var dataMatch = (!dataInicioObj || dataVencimento >= dataInicioObj) && (!dataFimObj || dataVencimento <= dataFimObj);

      tr[i].style.display = descricaoObservacaoMatch && tagMatch && contaContabilMatch && mesMatch && naturezaMatch && dataMatch ? "" : "none";
  }
  calcularSaldoAcumulado();
}

// Adiciona ouvintes de evento para as caixas de pesquisa e seleção de conta contábil
document.getElementById('caixa-pesquisa').addEventListener('keyup', filtrarTabela);
document.getElementById('caixa-pesquisa-tags').addEventListener('keyup', filtrarTabela);
document.getElementById('contas-contabeis').addEventListener('change', filtrarTabela);
document.getElementById('meses').addEventListener('change', filtrarTabela);
document.getElementById('natureza').addEventListener('change', filtrarTabela);
document.getElementById('data-inicio').addEventListener('change', filtrarTabela);
document.getElementById('data-fim').addEventListener('change', filtrarTabela);


// Calcula o saldo total dos bancos, sem filtragem
document.addEventListener("DOMContentLoaded", function() {
  atualizarSaldoTotalBancos();
});

function atualizarSaldoTotalBancos() {
  var linhasBanco = document.querySelectorAll(".row-bancos");
  var saldoTotal = 0;

  linhasBanco.forEach(function(linha) {
    var celulaSaldo = linha.querySelector(".saldo-banco-row");
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

  linhasFluxoCaixa.forEach(function(linha) {
    var debitoCelula = linha.querySelector(".debito-row");
    var creditoCelula = linha.querySelector(".credito-row");
    var debito = debitoCelula && debitoCelula.textContent ? parseSaldo(debitoCelula.textContent) : 0;
    var credito = creditoCelula && creditoCelula.textContent ? parseSaldo(creditoCelula.textContent) : 0;
    
    saldoAtual += credito - debito;
    
    var saldoCelula = linha.querySelector(".saldo-row");
    if (saldoCelula) {
      saldoCelula.textContent = formatarComoMoeda(saldoAtual);
    }
    else {
      linha.style.display = "none"; 
    }
  });
}

// Calcular o saldo total dos bancos que estão sendo filtrados
function filtrarBancos() {
  var selectBancos = document.getElementById("bancos");
  var bancoSelecionadoId = selectBancos.value; // O valor (ID) do banco selecionado
  
  var tabelaBancos = document.getElementById("box-grid-bancos").getElementsByTagName("tbody")[0];
  var linhas = tabelaBancos.getElementsByTagName("tr");
  
  var saldoTotal = 0; // Inicializa o saldo total como 0
  
  for (var i = 0; i < linhas.length; i++) {
    if (linhas[i].classList.contains("row-bancos")) {
      var bancoLinhaId = linhas[i].getAttribute("data-banco-id");
      
      if (bancoSelecionadoId === "Todos" || bancoLinhaId === bancoSelecionadoId) {
        linhas[i].style.display = ""; // Mostra a linha se corresponder ao filtro
        
        // Adiciona o saldo do banco ao saldo total
        var saldoBanco = linhas[i].getElementsByClassName("saldo-banco-row")[0].textContent;
        saldoBanco = parseFloat(saldoBanco.replace(/\./g, '').replace(',', '.'));
        saldoTotal += saldoBanco;
      } else {
        linhas[i].style.display = "none"; // Esconde a linha se não corresponder ao filtro
      }
    }
  }
  
  atualizarSaldosFluxoCaixa(saldoTotal); // Certifique-se de que esta função é chamada apenas uma vez, após o loop
  
  // Atualiza o saldo total na linha de totais
  var saldoTotalBancoRow = document.querySelector(".saldo-total-banco-row");
  if (saldoTotalBancoRow) {
    saldoTotalBancoRow.textContent = saldoTotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }
}

document.getElementById('bancos').addEventListener('change', filtrarBancos);



function calcularSaldoAcumulado() {
  // Obtem o saldo inicial total dos bancos.
  var saldoTotalBancoRow = document.querySelector(".saldo-total-banco-row");
  var saldoInicial = saldoTotalBancoRow ? parseSaldo(saldoTotalBancoRow.textContent) : 0;
  var saldoAtual = saldoInicial;
  
  // Seleciona todas as linhas visíveis do fluxo de caixa.
  var linhasFluxoCaixa = document.querySelectorAll("#tabela-lancamentos .row-lancamentos");
  
  linhasFluxoCaixa.forEach(function(linha) {
    if (linha.style.display !== "none") {
      var debitoCelula = linha.querySelector(".debito-row");
      var creditoCelula = linha.querySelector(".credito-row");
      var debito = debitoCelula && debitoCelula.textContent ? parseSaldo(debitoCelula.textContent) : 0;
      var credito = creditoCelula && creditoCelula.textContent ? parseSaldo(creditoCelula.textContent) : 0;
      
      // Calcula o saldo atual baseado no saldo anterior, créditos e débitos.
      saldoAtual += credito - debito;
      
      // Atualiza a célula de saldo da linha atual.
      var saldoCelula = linha.querySelector(".saldo-row");
      if (saldoCelula) {
        saldoCelula.textContent = formatarComoMoeda(saldoAtual);
      }
    }
  });
}

function parseSaldo(valorSaldo) {
  var numero = valorSaldo.replace('R$', '').trim().replace(/\./g, '').replace(',', '.');
  return parseFloat(numero) || 0;
}

function formatarComoMoeda(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}