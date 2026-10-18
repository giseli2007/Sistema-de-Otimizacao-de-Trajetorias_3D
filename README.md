# Otimização de trajetória 3D com restrições topográficas

Repositório único com duas partes que só conversam por HTTP:

- `web/`: visualização do mapa em plano/3D (pronta). Veja `web/README.md`.
- Núcleo Python (esqueleto): `calclib/`, `terreno/`, `vias/`, `model/`, `planner/`, `viz/`.
- `servidor/`: serve o `web/` e, futuramente, expõe a API (`rotas.py`) que liga o mapa ao núcleo.

## Rodar a visualização
    py servidor/servir.py        # ou python3 servidor/servir.py
    # abrir http://localhost:8000

## Regra de dependência (de baixo para cima)
`calclib` <- `terreno`, `vias`, `model` <- `planner` <- `servidor`

O `web/` nunca importa Python e o Python não sabe que existe um navegador. O planejador fica testável sem abrir o mapa
(`terreno/synthetic.py` + `tests/`).

## Fonte de relevo
O mapa usa tiles públicos (AWS Terrain Tiles e Mapterhorn), sem baixar arquivos. O planejador deve usar os mesmos tiles
(`terreno/terrarium.py`) para que o que você vê seja o que foi planejado. Ao devolver uma rota, a API deve informar a fonte usada.

## Estado
| Parte                                             | Situação  |
|---------------------------------------------------|-----------|
| `web/` (mapa, 3D automático, DEMs, recorte)       | pronto    |
| `servidor/servir.py`                              | pronto    |
| `calclib`, `terreno`, `vias`, `model`, `planner`, `viz`, `servidor/rotas.py`, `web/js/{api,trajetoria,gpx,vias}.js` | esqueleto |
