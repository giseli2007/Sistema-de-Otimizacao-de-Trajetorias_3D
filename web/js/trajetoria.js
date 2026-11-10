
export function iniciarTrajetoria(map) {

  // BOTÕES DA INTERFACE
  const botaoPlanejamento = document.getElementById("iniciarPlanejamento");
  const botaoCamadas = document.getElementById("camadas");
  const botaoRelevo = document.getElementById("controleRelevo");
  const botaoLimpar = document.getElementById("limparTrajetoria");
  const botaoFechar = document.getElementById("fecharPlanejamento");
  const botaoCalcular = document.getElementById("calcularTrajetoria");

  // MENUS
  const painelPlanejamento = document.getElementById("painelPlanejamento");
  const menuCamadas = document.getElementById("menuCamadas");
  const menuRelevo = document.getElementById("menuRelevo");

  const menus = [
    painelPlanejamento,
    menuCamadas,
    menuRelevo
  ];

  // INFORMAÇÕES DOS PONTOS
  const coordenadaInicial = document.getElementById("coordenadaInicial");
  const coordenadaFinal = document.getElementById("coordenadaFinal");
  const status = document.getElementById("statusTrajetoria");

  // RESULTADOS
  const comprimento = document.getElementById("comprimentoTrajetoria");
  const inclinacao = document.getElementById("inclinacaoMaxima");
  const energia = document.getElementById("energiaEstimada");
  const nosExpandidos = document.getElementById("nosExpandidos");
  const cartaoResultados = document.getElementById("resultadosTrajetoria");
  const botaoMinimizar = document.getElementById("minimizarResultados");

  // ESTADO DA SELEÇÃO
  let pontoInicial = null;
  let pontoFinal = null;
  let marcadorInicial = null;
  let marcadorFinal = null;
  let selecionandoPontos = false;

  // FECHA TODOS OS MENUS
  function fecharMenus() {
    menus.forEach(menu => menu.classList.remove("aberto"));
  }
  // Fecha os menus pelos botões com data-fechar
  document.querySelectorAll("[data-fechar]").forEach(botao => {
    botao.addEventListener("click", () => {
      const idMenu = botao.dataset.fechar;
      const menu = document.getElementById(idMenu);

      if (menu) {
        menu.classList.remove("aberto");
      }
    });
  });
  // ABRE UM MENU E FECHA OS OUTROS
  function alternarMenu(menuSelecionado) {
    const estavaAberto = menuSelecionado.classList.contains("aberto");

    fecharMenus();

    if (!estavaAberto) {
      menuSelecionado.classList.add("aberto");
    }
  }

  // ABRE O PLANEJAMENTO
  botaoPlanejamento.addEventListener("click", () => {
    alternarMenu(painelPlanejamento);

    selecionandoPontos =
      painelPlanejamento.classList.contains("aberto") &&
      !pontoFinal;

    if (selecionandoPontos) {
      status.textContent = pontoInicial
        ? "Clique no mapa para escolher o destino."
        : "Clique no mapa para escolher o ponto inicial.";
    }
  });
  // Minimiza ou restaura o cartão de resultados
  botaoMinimizar.addEventListener("click", () => {
    cartaoResultados.classList.toggle("minimizado");

    const minimizado =
      cartaoResultados.classList.contains("minimizado");

    botaoMinimizar.textContent = minimizado ? "+" : "−";

    botaoMinimizar.title = minimizado
      ? "Restaurar resultados"
      : "Minimizar resultados";
  });

  // ABRE O MENU DE CAMADAS
  botaoCamadas.addEventListener("click", () => {
    alternarMenu(menuCamadas);
    selecionandoPontos = false;
  });

  // ABRE O MENU DE RELEVO
  botaoRelevo.addEventListener("click", () => {
    alternarMenu(menuRelevo);
    selecionandoPontos = false;
  });

  // FECHA O PAINEL DE PLANEJAMENTO
  botaoFechar.addEventListener("click", () => {
    fecharMenus();
    selecionandoPontos = false;
  });

  // CRIA UM MARCADOR
  function criarMarcador(coordenadas, tipo) {
    const elemento = document.createElement("div");
    elemento.className = `marcadorTrajetoria ${tipo}`;

    return new maplibregl.Marker({
      element: elemento
    })
      .setLngLat(coordenadas)
      .addTo(map);
  }

  // RECEBE OS CLIQUES NO MAPA
  map.on("click", (evento) => {

    if (!selecionandoPontos) return;

    const coordenadas = [
      evento.lngLat.lng,
      evento.lngLat.lat
    ];

    // PRIMEIRO CLIQUE: PONTO INICIAL
    if (!pontoInicial) {
      pontoInicial = coordenadas;

      marcadorInicial = criarMarcador(
        coordenadas,
        "marcadorInicial"
      );

      coordenadaInicial.textContent =
        `${coordenadas[1].toFixed(6)}, ${coordenadas[0].toFixed(6)}`;

      status.textContent =
        "Ponto inicial definido. Agora escolha o destino.";

      return;
    }

    // SEGUNDO CLIQUE: PONTO FINAL
    if (!pontoFinal) {

      if (
        coordenadas[0] === pontoInicial[0] &&
        coordenadas[1] === pontoInicial[1]
      ) {
        status.textContent =
          "Escolha um destino diferente do ponto inicial.";
        return;
      }

      pontoFinal = coordenadas;

      marcadorFinal = criarMarcador(
        coordenadas,
        "marcadorFinal"
      );

      coordenadaFinal.textContent =
        `${coordenadas[1].toFixed(6)}, ${coordenadas[0].toFixed(6)}`;

      botaoCalcular.disabled = false;
      selecionandoPontos = false;

      status.textContent =
        "Pontos definidos! Você já pode calcular a trajetória.";
    }
  });

  // LIMPA OS RESULTADOS
  function limparResultados() {
    comprimento.textContent = "—";
    inclinacao.textContent = "—";
    energia.textContent = "—";
    nosExpandidos.textContent = "—";

    cartaoResultados.classList.remove("visivel");
  }

  // LIMPA OS PONTOS E REINICIA A SELEÇÃO
  function limparTrajetoria() {

    if (marcadorInicial) marcadorInicial.remove();
    if (marcadorFinal) marcadorFinal.remove();

    marcadorInicial = null;
    marcadorFinal = null;

    pontoInicial = null;
    pontoFinal = null;

    coordenadaInicial.textContent = "Aguardando seleção";
    coordenadaFinal.textContent = "Aguardando seleção";

    botaoCalcular.disabled = true;

    limparResultados();

    fecharMenus();
    painelPlanejamento.classList.add("aberto");

    selecionandoPontos = true;

    status.textContent =
      "Clique no mapa para escolher o ponto inicial.";
  }

  botaoLimpar.addEventListener("click", limparTrajetoria);

  // PREPARA OS DADOS PARA O ALGORITMO
  botaoCalcular.addEventListener("click", () => {

    if (!pontoInicial || !pontoFinal) {
      status.textContent =
        "Selecione os dois pontos antes de calcular.";
      return;
    }

    const algoritmo = document.getElementById("algoritmo");

    const dadosTrajetoria = {
      pontoInicial: {
        latitude: pontoInicial[1],
        longitude: pontoInicial[0]
      },

      pontoFinal: {
        latitude: pontoFinal[1],
        longitude: pontoFinal[0]
      },

      algoritmo: algoritmo.value
    };

    limparResultados();

    console.log("Dados da trajetória:", dadosTrajetoria);

    status.textContent =
      "Pontos enviados para preparação do cálculo. Aguardando integração com o algoritmo.";
  });

}
