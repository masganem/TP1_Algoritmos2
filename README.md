# Projeto de Análise de Dados de Estabelecimentos

## Executando
```bash
pip install -r requirements.txt
python compile.py build_ext --inplace
python main.py
```

### Location Data Parser (`parse_and_geocode.py`)
- Puxa dados dos estabelecimentos da prefeitura
- Limpa os dados para manter apenas restaurantes e bares
- Utiliza a API do OpenStreetView para obter coordenadas geográficas a partir do endereço
- Utiliza o dataframe `useful_bars_dataset` (formato simplificado do endereço para melhor compatibilidade com a API)
- Necessário cruzar com a tabela `final_bars_and_restaurants` e remover a coluna `useful_address`

### Geocoding (`parse_and_geocode.py`)
- A função de obtenção de coordenadas já foi executada
- Output salvo em `geocoded_bars_and_restaurants.csv`
- Observação: Alguns estabelecimentos não tiveram suas coordenadas obtidas, mas a maioria dos registros está completa

### Implementação da KD-Tree (`kd_tree.cpp`)
- Construtor recebe lista de coordenadas (`vector<pair<latitude, longitude>>`)
- Ordenação in-place (complexidade: O(n log²(n)))
- Método público para range search com 4 parâmetros (limites de latitude e longitude)
- O módulo é compilado para Python com a ajuda do script `compile.py`

### Próximos Passos - Comida di Buteco
- Necessário cruzar com dados do Comida di Buteco
- Desafio: Diferenças na escrita dos nomes entre o site e registros da prefeitura
- Solução proposta:
  1. Baixar CSV com nomes dos bares do Comida di Buteco
  2. Utilizar OpenStreetView API novamente (mais tolerante a variações de escrita)
  3. Realizar join com a tabela existente usando coordenadas
  4. Adicionar coluna booleana indicando participação no Comida di Buteco

-----

### Justificativa das dependências utilizadas:
| Dependência | Finalidade |
| --- | --- |
| dash-leaflet | Construção da interface Web |
| pybind11 | Compilação da K-D Tree para um módulo Python |
| bs4 | Web scraping para obtenção dos dados do [Comida di Buteco](https://comidadibuteco.com.br) |
