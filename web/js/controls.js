// Liga o painel (index.html) ao mapa. Novo controle = novo elemento no HTML + um handler aqui.
import { BASES, BASE_PADRAO, DEMS, DEM_ATIVO } from './config.js';
import { reconstruir } from './style.js';

const $ = id => document.getElementById(id);
const opcoes = obj => Object.entries(obj).map(([id, o]) => `<option value="${id}">${o.nome}</option>`).join('');

export function iniciarControles(map, terreno) {
  const ex = $('ex'), base = $('base'), dem = $('dem');

  base.innerHTML = opcoes(BASES);
  base.value = BASE_PADRAO;
  base.onchange = () => {
    for (const id of Object.keys(BASES))
      map.setLayoutProperty(id, 'visibility', id === base.value ? 'visible' : 'none');
  };

  dem.innerHTML = opcoes(DEMS);
  dem.value = DEM_ATIVO;
  dem.onchange = () => reconstruir(map, terreno);   // troca a fonte de relevo, mantendo recorte, base e sombreado

  $('hs').onchange = e =>
    map.setLayoutProperty('hillshade', 'visibility', e.target.checked ? 'visible' : 'none');

  ex.oninput = () => {
    $('exv').textContent = (+ex.value).toFixed(1).replace('.', ',') + '×';
    terreno.definirExagero(+ex.value);
  };
}
