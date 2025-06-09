# Projeto de Análise de Dados de Estabelecimentos
Alunos: Marcelo Augusto Salomão Ganem, Rafael Prado Paniago, Pedro Loures Alzamora 

O projeto pode ser visitado em https://tp1-algoritmos2.onrender.com

[mapa (1).webm](https://github.com/user-attachments/assets/f032e9ff-fe36-4a3b-bb0c-c60d4ca1100d)
## Executando
```bash
pip install -r requirements.txt
python kd_tree/compile.py build_ext --inplace
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

### Deduplicação (`dedup_geocoded.py`)
- Deduplica entradas com base no nome. Isso reduz a base original de 13625 a 12869 entradas.

### Implementação da KD-Tree (`kd_tree/`)
##### `kd_tree/KDTree.py`
- Envelopa a implementação da K-D Tree em C++
##### `kd_tree/kd_tree.cpp`
- Construtor recebe lista de coordenadas (`vector<pair<latitude, longitude>>`)
- Ordenação in-place (complexidade: O(n log²(n)))
- Método público para range search com 4 parâmetros (limites de latitude e longitude)
- O módulo é compilado para Python com a ajuda do script `compile.py`

### Comida di Buteco (`comida_di_buteco/`)
Os dados foram extraídos utilizando a biblioteca [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/). Vale observar que as "informações sobre o prato", conforme o enunciado, se limitam às imagens disponíveis na [galeria de restaurantes](https://comidadibuteco.com.br/butecos/belo-horizonte/) -- isso porque as páginas dos estabelecimentos específicos ([exemplo](https://comidadibuteco.com.br/buteco/amarelim-do-prado/)) não estão sendo carregadas desde (pelo menos) 03/07/2025.
- **Casamento** (`comida_di_buteco/align_data.py`): aplica normalizações de string e tenta fazer um _join_ entre os endereços dos dados coletados (`butecos.csv`) e os dados da PBH com base em endereço e nome.
##### Próximos Passos
- Caso restaurante esteja no comida de buteco,
    - Mostrar popup com imagem do prato concorrente
    - Highlight na tabela

-----

### Justificativa das dependências utilizadas:
| Dependência | Finalidade |
| --- | --- |
| dash-leaflet | Construção da interface Web |
| geopy | Extração de dados geográficos dos bares/restaurantes |
| pybind11 | Compilação da K-D Tree para um módulo Python |
| bs4 | Web scraping para obtenção dos dados do [Comida di Buteco](https://comidadibuteco.com.br) |
