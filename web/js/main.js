// Ponto de entrada: cria o mapa e conecta os módulos.
import { VIEW, CARGA } from './config.js';
import { criarEstilo } from './style.js';
import { criarTerreno } from './terrain.js';
import { iniciarControles } from './controls.js';
import { iniciarHud } from './hud.js';
import { iniciarArea } from './area.js';

const map = new maplibregl.Map({
  container: 'map',
  style: criarEstilo(),
  center: VIEW.center,
  zoom: VIEW.zoom,
  maxZoom: VIEW.maxZoom,
  maxPitch: VIEW.maxPitch,
  renderWorldCopies: CARGA.renderWorldCopies,
  refreshExpiredTiles: CARGA.refreshExpiredTiles,
  hash: true                         // posição na URL
});
map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-right');
map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');

const terreno = criarTerreno(map);
iniciarControles(map, terreno);
iniciarHud(map, terreno, document.getElementById('hud'));
iniciarArea(map, terreno);
