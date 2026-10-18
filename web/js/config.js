// Tudo que você mais vai querer ajustar fica aqui.

// Posição inicial e câmera
export const VIEW = {
  center: [-44.64, -22.38],  // [longitude, latitude]
  zoom: 12,
  maxZoom: 18,
  maxPitch: 75              // padrão do MapLibre é 60. Acima de ~72° o horizonte aparece e a carga de tiles dispara (veja CARGA)
};

// Fontes de relevo (DEM), todas em codificação "terrarium". O seletor do painel lista todas.
// O que limita o detalhe do 3D é a resolução REAL dos dados, não o zoom:
//  - aws: ~30 m na maior parte do mundo (SRTM, NASADEM...), tiles até z15.
//  - mapterhorn: global de 30 m (Copernicus), até z12. É a fonte que o gpx.studio usa hoje.
//  - mapterhorn-alta: mesma fonte, pedindo tiles até z17 (0,25 a 10 m). SÓ funciona onde há dado de alta
//    resolução (Europa, Japão, EUA, parte do Canadá/Austrália/Nova Zelândia...): https://mapterhorn.com/coverage
//    Fora dessas áreas os tiles z13+ não existem e o relevo falha; use as outras duas.
export const DEM_ATIVO = 'aws';
const CREDITO_MAPTERHORN = '<a href="https://mapterhorn.com/attribution">© Mapterhorn</a>';
export const DEMS = {
  aws: {
    nome: 'AWS (~30 m)',
    tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
    tileSize: 256, maxzoom: 15,
    attribution: 'Relevo: AWS Terrain Tiles (SRTM, NASADEM e outros)'
  },
  mapterhorn: {
    nome: 'Mapterhorn global (30 m)',
    tiles: ['https://tiles.mapterhorn.com/{z}/{x}/{y}.webp'],
    tileSize: 512, maxzoom: 12, attribution: CREDITO_MAPTERHORN
  },
  'mapterhorn-alta': {
    nome: 'Mapterhorn alta resolução (só onde há cobertura)',
    url: 'https://tiles.mapterhorn.com/tilejson.json',
    tileSize: 512, attribution: CREDITO_MAPTERHORN
  }
};

// Mapas base. O "id" vira camada do MapLibre; "nome" aparece no seletor.
// maxzoom: acima dele o tile é reaproveitado (esticado) em vez de ficar em branco.
export const BASES = {
  topo: { nome: 'Topográfico', maxzoom: 17,
          tiles: ['a', 'b', 'c'].map(s => `https://${s}.tile.opentopomap.org/{z}/{x}/{y}.png`),
          attribution: '© OpenTopoMap (CC-BY-SA), © OpenStreetMap' },
  sat:  { nome: 'Satélite', maxzoom: 19,
          tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
          attribution: 'Imagens © Esri, Maxar, Earthstar Geographics' },
  osm:  { nome: 'Ruas', maxzoom: 19,
          tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
          attribution: '© OpenStreetMap contributors' }
};
export const BASE_PADRAO = 'topo';

// Céu e névoa (só aparecem com o mapa inclinado). Tudo preto; o fundo da página também (css/style.css, --canvas).
export const SKY = {
  'sky-color': '#000000', 'sky-horizon-blend': 0.5,
  'horizon-color': '#000000', 'horizon-fog-blend': 0.6,
  'fog-color': '#000000', 'fog-ground-blend': 0.4,
  'atmosphere-blend': 0
};

// Carregamento. O MapLibre já pede só os tiles que aparecem na tela (e cancela os pedidos que ficaram para trás
// ao dar zoom); estes são os ajustes extras para poupar rede e GPU.
export const CARGA = {
  fadeRaster: 0,               // ms do "fade-in" de cada tile de imagem (padrão 300). 0 = o tile aparece na hora
  refreshExpiredTiles: false,  // não rebaixa tiles "vencidos" que continuam na tela
  renderWorldCopies: false     // não desenha cópias repetidas do mundo em zooms baixos
};
