# Otimização de trajetória 3D com restrições topográficas

Repositório único com duas partes que só conversam por HTTP:

- `web/`: visualização do mapa em plano/3D (pronta). Veja `web/README.md`.
- Núcleo Python (esqueleto): `calclib/`, `terreno/`, `vias/`, `model/`, `planner/`, `viz/`.
- `servidor/`: serve o `web/` e, futuramente, expõe a API (`rotas.py`) que liga o mapa ao núcleo.

## Rodar a visualização
    py servidor/servir.py  
    
    #ou python3 servidor/servir.py
    
    #abrir http://localhost:8000
