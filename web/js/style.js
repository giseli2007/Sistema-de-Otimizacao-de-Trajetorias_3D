// Monta o estilo do MapLibre (fontes + camadas) a partir de config.js.
// bounds [oeste, sul, leste, norte]: se informado, nenhuma fonte pede tiles fora dessa caixa (usado no recorte de área).
import { BASES, BASE_PADRAO, DEMS, DEM_ATIVO, SKY, CARGA } from './config.js';

export function criarEstilo({ bounds, dem: idDem = DEM_ATIVO, base = BASE_PADRAO, sombreado = true } = {}) {
  const extra = bounds ? { bounds } : {};
  const { nome, ...def } = DEMS[idDem];
  const dem = { type: 'raster-dem', encoding: 'terrarium', ...def, ...extra };
  const { attribution, ...demSemCredito } = dem;     // evita créditos duplicados

  const sources = { dem, 'dem-hs': demSemCredito };  // 'dem-hs' alimenta só o sombreado
  const layers = [];

  for (const [id, { nome, ...b }] of Object.entries(BASES)) {
    sources[id] = { type: 'raster', tileSize: 256, ...b, ...extra };
    layers.push({ id, type: 'raster', source: id, layout: { visibility: id === base ? 'visible' : 'none' },
                  paint: { 'raster-fade-duration': CARGA.fadeRaster } });
  }
  layers.push({
    id: 'hillshade', type: 'hillshade', source: 'dem-hs',
    layout: { visibility: sombreado ? 'visible' : 'none' },
    paint: { 'hillshade-exaggeration': 0.35, 'hillshade-shadow-color': '#1d2a24' }
  });

  return { version: 8, sources, layers, sky: SKY };
}

// Recria fontes e camadas lendo o estado do painel (DEM, mapa base, sombreado) e aplicando o recorte "bounds".
// Chamada sem bounds, mantém o recorte atual; com null, remove o recorte.
let limite = null;
export function reconstruir(map, terreno, bounds = limite) {
  limite = bounds;
  const $ = id => document.getElementById(id);
  const { sources, layers } = criarEstilo({ bounds, dem: $('dem').value, base: $('base').value, sombreado: $('hs').checked });
  map.setTerrain(null);                                   // o terreno precisa soltar a fonte antes de removê-la
  for (const l of [...layers].reverse()) map.removeLayer(l.id);
  for (const id of Object.keys(sources)) map.removeSource(id);
  for (const [id, s] of Object.entries(sources)) map.addSource(id, s);
  const antes = map.getLayer('area-mascara') ? 'area-mascara' : undefined;   // mantém a máscara por cima
  for (const l of layers) map.addLayer(l, antes);
  terreno.aplicar();                                      // religa o terreno se o mapa estiver inclinado
}
