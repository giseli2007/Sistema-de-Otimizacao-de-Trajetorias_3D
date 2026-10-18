// Relevo 3D automático: com o mapa inclinado (pitch > LIMIAR) o terreno liga; sem inclinação, o mapa fica plano.
// Dispara o evento 'modochange' no mapa sempre que o terreno muda.
const LIMIAR = 0.5;   // graus. Tolerância para o "zero" (zerar o pitch no mouse é difícil; a bússola também zera)

export function criarTerreno(map) {
  const t = {
    ligado: false,
    exagero: 1,
    aplicar() {
      map.setTerrain(t.ligado ? { source: 'dem', exaggeration: t.exagero } : null);
      map.fire('modochange');
    },
    atualizar() {
      const on = map.getPitch() > LIMIAR;
      if (on !== t.ligado) { t.ligado = on; t.aplicar(); }
    },
    definirExagero(v) { t.exagero = v; if (t.ligado) t.aplicar(); }
  };
  map.on('pitch', t.atualizar);
  map.on('load', t.atualizar);   // a posição inicial vinda da URL (#hash) pode já ter inclinação
  return t;
}
