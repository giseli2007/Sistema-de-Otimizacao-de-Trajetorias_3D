// Seleção de área: desenha um retângulo e recorta o mapa para mostrar SOMENTE essa parte.
import { VIEW } from './config.js';
import { reconstruir } from './style.js';

const MUNDO = [[-180, -85], [180, -85], [180, 85], [-180, 85], [-180, -85]];
const anel = ([w, s, e, n]) => [[w, s], [e, s], [e, n], [w, n], [w, s]];
const caixa = (a, b) => [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])];
const vazio = { type: 'FeatureCollection', features: [] };
const $ = id => document.getElementById(id);
const fmt = x => Math.round(x).toLocaleString('pt-BR');

export function iniciarArea(map, terreno) {
  const info = $('info'), bSel = $('sel'), bTudo = $('tudo');
  let bbox = null, inicio = null, atual = null, selecionando = false, dimensoes = '';

  map.on('load', () => {
    map.addSource('area', { type: 'geojson', data: vazio });
    map.addLayer({ id: 'area-mascara', type: 'fill', source: 'area', filter: ['==', ['get', 'tipo'], 'mascara'],
                   paint: { 'fill-color': '#000000', 'fill-opacity': 0.4 } });   // escurece enquanto desenha
    map.addLayer({ id: 'area-borda', type: 'line', source: 'area', filter: ['==', ['get', 'tipo'], 'borda'],
                   paint: { 'line-color': '#ffd54a', 'line-width': 2 } });
  });

  const desenhar = b => map.getSource('area').setData(!b ? vazio : { type: 'FeatureCollection', features: [
    { type: 'Feature', properties: { tipo: 'mascara' }, geometry: { type: 'Polygon', coordinates: [MUNDO, anel(b)] } },
    { type: 'Feature', properties: { tipo: 'borda' },   geometry: { type: 'Polygon', coordinates: [anel(b)] } }
  ] });

  const mascara = (cor, opac) => {
    map.setPaintProperty('area-mascara', 'fill-color', cor);
    map.setPaintProperty('area-mascara', 'fill-opacity', opac);
  };

  const mostrarTudo = () => {
    if (!bbox) return;
    bbox = null; desenhar(null); reconstruir(map, terreno, null); mascara('#000000', 0.4);
    bTudo.disabled = true; info.textContent = '';
  };

  // --- desenhar o retângulo (mouse e toque) ---
  const pt = e => [e.lngLat.lng, e.lngLat.lat];
  const ini = e => { if (selecionando) inicio = atual = pt(e); };
  const mov = e => { if (selecionando && inicio) { atual = pt(e); desenhar(caixa(inicio, atual)); } };
  const fim = () => {
    if (!selecionando || !inicio) return;
    const b = caixa(inicio, atual);
    inicio = null; selecionando = false;
    map.dragPan.enable(); map.getCanvas().style.cursor = '';
    if (b[2] - b[0] < 1e-4 || b[3] - b[1] < 1e-4) { desenhar(null); info.textContent = ''; return; }  // clique sem arrastar

    bbox = b;
    desenhar(b);
    // fora da área: cor de fundo da página, opaca (também esconde a sobra de tiles na borda)
    mascara(getComputedStyle(document.body).backgroundColor, 1);
    reconstruir(map, terreno, b);
    bTudo.disabled = false;

    const kmL = (b[2] - b[0]) * 111.32 * Math.cos(((b[1] + b[3]) / 2) * Math.PI / 180);
    const kmA = (b[3] - b[1]) * 110.57;
    dimensoes = `Área: ${kmL.toFixed(1).replace('.', ',')} × ${kmA.toFixed(1).replace('.', ',')} km`;
    info.textContent = dimensoes;

    map.fitBounds([[b[0], b[1]], [b[2], b[3]]],
      { padding: 60, pitch: map.getPitch(), bearing: map.getBearing(), duration: 1200, maxZoom: VIEW.maxZoom });
    map.once('moveend', () => map.once('idle', medirRelevo));
  };
  for (const [tipo, f] of [['mousedown', ini], ['touchstart', ini], ['mousemove', mov],
                           ['touchmove', mov], ['mouseup', fim], ['touchend', fim]]) map.on(tipo, f);

  bSel.onclick = () => {
    mostrarTudo();                                  // para escolher outra região, volta ao mapa completo
    selecionando = true; map.dragPan.disable(); map.getCanvas().style.cursor = 'crosshair';
    info.textContent = 'Arraste no mapa para desenhar a área.';
  };
  bTudo.onclick = mostrarTudo;

  // Amostra uma grade 31×31 dentro da área (só funciona com o 3D ligado e os tiles carregados)
  const medirRelevo = () => {
    if (!bbox) return;
    const [w, s, e, n] = bbox, v = [];
    for (let i = 0; i <= 30; i++) for (let j = 0; j <= 30; j++) {
      const h = map.queryTerrainElevation([w + (e - w) * i / 30, s + (n - s) * j / 30]);
      if (h != null) v.push(h / terreno.exagero);
    }
    if (!v.length) return;
    const lo = Math.min(...v), hi = Math.max(...v);
    info.textContent = `${dimensoes} · Altitude ${fmt(lo)}–${fmt(hi)} m (desnível ${fmt(hi - lo)} m)`;
  };
  map.on('modochange', () => { if (bbox && terreno.ligado) map.once('idle', medirRelevo); });
}
