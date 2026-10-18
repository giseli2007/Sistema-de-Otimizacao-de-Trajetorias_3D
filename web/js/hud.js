// Faixa inferior: altitude sob o cursor, zoom e inclinação.
export function iniciarHud(map, terreno, el) {
  let cursor = null;

  const atualizar = () => {
    let alt = '—';
    if (terreno.ligado && cursor) {
      const h = map.queryTerrainElevation(cursor);        // vem multiplicada pelo exagero
      if (h != null) alt = Math.round(h / terreno.exagero).toLocaleString('pt-BR') + ' m';
    }
    el.textContent = `Altitude ${alt} · Zoom ${map.getZoom().toFixed(1)} · Inclinação ${Math.round(map.getPitch())}°`;
  };

  map.on('mousemove', e => { cursor = e.lngLat; atualizar(); });
  map.on('move', atualizar);
  map.on('modochange', atualizar);
  atualizar();
}
