# web/: visualização do mapa (MapLibre, sem build)

Plano/3D automático pela inclinação, três fontes de relevo (DEM), três mapas base, recorte de área.
Tudo roda no navegador e o relevo vem de tiles públicos: nenhum dado é baixado.

## Rodar (da raiz do projeto)
    py servidor/servir.py        # Windows (ou python3 servidor/servir.py)
    # abrir http://localhost:8000

## Onde mexer
| Quero...                                | Arquivo                          |
|-----------------------------------------|----------------------------------|
| Local inicial, zoom, inclinação máxima  | js/config.js (VIEW)              |
| Fontes de relevo e DEM padrão           | js/config.js (DEMS, DEM_ATIVO)   |
| Adicionar mapa base                     | js/config.js (BASES)             |
| Fontes e camadas do mapa                | js/style.js                      |
| Comportamento do 3D automático          | js/terrain.js                    |
| Seleção e recorte de área               | js/area.js                       |
| Novo botão/slider                       | index.html + js/controls.js      |
| Faixa de altitude/zoom                  | js/hud.js                        |
| Aparência                               | css/style.css                    |

## Módulos ainda vazios (esqueleto)
js/api.js (chamadas ao backend), js/trajetoria.js (rota 3D), js/gpx.js (GPX), js/vias.js (classificação de vias).

## Carregamento e névoa
- `js/config.js` → `CARGA`: fade dos tiles, renovação de tiles vencidos, cópias do mundo.
- `js/config.js` → `VIEW.maxPitch` (75): é o ajuste que mais pesa. Quanto mais inclinado, mais tiles distantes são pedidos.
- `js/config.js` → `SKY`: céu e névoa (pretos). O fundo da página é `--canvas` em `css/style.css`.
