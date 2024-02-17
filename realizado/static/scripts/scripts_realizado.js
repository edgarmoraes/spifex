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
  var filtroBancoLiquidacao = document.getElementById("bancos").value.toUpperCase();
  var filtroNatureza = document.getElementById("natureza").value;

  var tabela = document.getElementById("tabela-lancamentos");
  var tr = tabela.getElementsByTagName("tr");

  var dataInicioObj = dataInicio ? new Date(dataInicio) : null;
  var dataFimObj = dataFim ? new Date(dataFim) : null;

  for (var i = 0; i < tr.length; i++) {
      var tdDescricao = tr[i].getElementsByClassName("descricao-row")[0];
      var tdObservacao = tr[i].getElementsByClassName("obs-row")[0];
      var contaContabil = tr[i].getAttribute('data-conta-contabil').toUpperCase();
      var bancoLiquidacao = tr[i].getAttribute('data-banco-liquidacao').toUpperCase();
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
      var bancoLiquidacaoMatch = filtroBancoLiquidacao === "" || bancoLiquidacao.toUpperCase().indexOf(filtroBancoLiquidacao) > -1;
      var mesMatch = (!inicioMesDate && !fimMesDate) || (dataVencimento >= inicioMesDate && dataVencimento <= fimMesDate);
      var naturezaMatch = filtroNatureza === "" || filtroNatureza === naturezaLancamento;
      var dataMatch = (!dataInicioObj || dataVencimento >= dataInicioObj) && (!dataFimObj || dataVencimento <= dataFimObj);

      tr[i].style.display = descricaoObservacaoMatch && tagMatch && contaContabilMatch && bancoLiquidacaoMatch && mesMatch && naturezaMatch && dataMatch ? "" : "none";
  }
  calcularSaldoAcumulado();
}

// Adiciona ouvintes de evento para as caixas de pesquisa e seleção de conta contábil
document.getElementById('caixa-pesquisa').addEventListener('keyup', filtrarTabela);
document.getElementById('caixa-pesquisa-tags').addEventListener('keyup', filtrarTabela);
document.getElementById('contas-contabeis').addEventListener('change', filtrarTabela);
document.getElementById('bancos').addEventListener('change', filtrarTabela);
document.getElementById('meses').addEventListener('change', filtrarTabela);
document.getElementById('natureza').addEventListener('change', filtrarTabela);
document.getElementById('data-inicio').addEventListener('change', filtrarTabela);
document.getElementById('data-fim').addEventListener('change', filtrarTabela);

// Saldo de bancos
document.addEventListener("DOMContentLoaded", function() {
  atualizarSaldoTotalBancos();
  filtrarFluxoCaixaPorBanco();
  document.getElementById('bancos').addEventListener('change', function() {
      filtrarBancos();
      filtrarFluxoCaixaPorBanco();
  });
});

function atualizarSaldoTotalBancos() {
  var linhasBanco = document.querySelectorAll(".row-bancos");
  var saldoTotal = parseSaldo(document.querySelector(".saldo-total-banco-row").textContent);

  linhasBanco.forEach(function(linha) {
      var saldoBanco = parseSaldo(linha.querySelector(".saldo-banco-row").textContent);
      saldoTotal += saldoBanco;
  });

  var saldoTotalBancoRow = document.querySelector(".saldo-total-banco-row");
  saldoTotalBancoRow.textContent = formatarComoMoeda(saldoTotal);
}

function filtrarBancos() {
  var bancoSelecionado = document.getElementById("bancos").value;
  var tabelaBancos = document.querySelectorAll(".row-bancos");
  var saldoTotal = 0;

  tabelaBancos.forEach(linha => {
      if (linha.querySelector(".banco-row").textContent === bancoSelecionado || bancoSelecionado === "") {
          linha.style.display = ""; 
          var saldo = parseSaldo(linha.querySelector(".saldo-banco-row").textContent);
          saldoTotal += saldo;
      } else {
          linha.style.display = "none"; 
      }
  });

  var saldoTotalBancoRow = document.querySelector(".saldo-total-banco-row");
  saldoTotalBancoRow.textContent = formatarComoMoeda(saldoTotal);
}

function filtrarFluxoCaixaPorBanco() {
  var bancoSelecionado = document.getElementById("bancos").value;
  var linhasFluxoCaixa = document.querySelectorAll("#tabela-lancamentos .row-lancamentos");
  var saldoTotal = parseSaldo(document.querySelector(".saldo-total-banco-row").textContent);

  for (var i = linhasFluxoCaixa.length - 1; i >= 0; i--) {
      var linha = linhasFluxoCaixa[i];
      var bancoLiquidacao = linha.getAttribute('data-banco-liquidacao');
      if (linha.style.display !== "none" && (bancoLiquidacao === bancoSelecionado || bancoSelecionado === "")) {
          var debito = parseSaldo(linha.querySelector(".debito-row").textContent || "0");
          var credito = parseSaldo(linha.querySelector(".credito-row").textContent || "0");
          
          saldoTotal += debito; // Débito é adicionado
          saldoTotal -= credito; // Crédito é subtraído

          var saldoCelula = linha.querySelector(".saldo-row");
          if (saldoCelula) {
              saldoCelula.textContent = formatarComoMoeda(saldoTotal);
          }
      }
  }
}

function parseSaldo(valorSaldo) {
  return parseFloat(valorSaldo.replace('R$', '').trim().replace(/\./g, '').replace(',', '.')) || 0;
}

function formatarComoMoeda(valor) {
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}