// Desenha a rota 3D sobre o terreno e o perfil de elevação.
// Status: esqueleto (sem implementação).
export {};

// Elementos do painel de trajetória
const pontoInicial = document.getElementById("pontoInicial");
const pontoFinal = document.getElementById("pontoFinal");
const algoritmo = document.getElementById("algoritmo");
const botaoCalcular = document.getElementById("calcularTrajetoria");

// Elementos dos resultados
const comprimento = document.getElementById("comprimentoTrajetoria");
const inclinacao = document.getElementById("inclinacaoMaxima");
const energia = document.getElementById("energiaEstimada");
const nosExpandidos = document.getElementById("nosExpandidos");
const statusTrajetoria = document.getElementById("statusTrajetoria");

// Converte as coordenadas digitadas em latitude e longitude
function interpretarCoordenadas(texto) {
  const coordenadas = texto.split(",");

  if (coordenadas.length !== 2) {
    return null;
  }

  const latitude = Number(coordenadas[0].trim());
  const longitude = Number(coordenadas[1].trim());

  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    return null;
  }

  if (latitude < -90 || latitude > 90) {
    return null;
  }

  if (longitude < -180 || longitude > 180) {
    return null;
  }

  return { latitude, longitude };
}

// Atualiza a mensagem de status
function atualizarStatus(mensagem) {
  statusTrajetoria.textContent = mensagem;
}

// Limpa os resultados anteriores
function limparResultados() {
  comprimento.textContent = "—";
  inclinacao.textContent = "—";
  energia.textContent = "—";
  nosExpandidos.textContent = "—";
}

// Evento do botão Calcular
botaoCalcular.addEventListener("click", () => {
  const inicio = interpretarCoordenadas(pontoInicial.value);
  const destino = interpretarCoordenadas(pontoFinal.value);

  // Verifica o ponto inicial
  if (!inicio) {
    atualizarStatus(
      "Coordenadas iniciais inválidas. Use latitude, longitude."
    );

    pontoInicial.focus();
    return;
  }

  // Verifica o ponto de destino
  if (!destino) {
    atualizarStatus(
      "Coordenadas de destino inválidas. Use latitude, longitude."
    );

    pontoFinal.focus();
    return;
  }

  // Verifica se os pontos são diferentes
  if (
    inicio.latitude === destino.latitude &&
    inicio.longitude === destino.longitude
  ) {
    atualizarStatus(
      "O ponto inicial e o destino precisam ser diferentes."
    );

    return;
  }

  // Prepara os dados para o algoritmo
  const dadosTrajetoria = {
    pontoInicial: inicio,
    pontoFinal: destino,
    algoritmo: algoritmo.value
  };

  limparResultados();

  console.log("Dados da trajetória:", dadosTrajetoria);

  atualizarStatus(
    "Coordenadas válidas. Aguardando integração com o algoritmo de busca."
  );

  // A chamada ao backend será adicionada quando conhecermos
  // o endpoint e o formato esperado pela equipe.
});
