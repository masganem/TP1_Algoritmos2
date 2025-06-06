# Projeto de Análise de Dados de Estabelecimentos

## O que foi feito até agora

### Location Data Parser
- Puxa dados dos estabelecimentos da prefeitura
- Limpa os dados para manter apenas restaurantes e bares
- Utiliza a API do OpenStreetView para obter coordenadas geográficas a partir do endereço
- Utiliza o dataframe `useful_bars_dataset` (formato simplificado do endereço para melhor compatibilidade com a API)
- Necessário cruzar com a tabela `final_bars_and_restaurants` e remover a coluna `useful_address`

### Status das Coordenadas
- A função de obtenção de coordenadas já foi executada
- Output salvo em `geocoded_bars_and_restaurantes.csv`
- Observação: Alguns estabelecimentos não tiveram suas coordenadas obtidas, mas a maioria dos registros está completa

### Próximos Passos - Comida di Buteco
- Necessário cruzar com dados do Comida di Buteco
- Desafio: Diferenças na escrita dos nomes entre o site e registros da prefeitura
- Solução proposta:
  1. Baixar CSV com nomes dos bares do Comida di Buteco
  2. Utilizar OpenStreetView API novamente (mais tolerante a variações de escrita)
  3. Realizar join com a tabela existente usando coordenadas
  4. Adicionar coluna booleana indicando participação no Comida di Buteco

### Implementação da KD-Tree
Localizada em `scratch.cpp`:
- Construtor recebe lista de coordenadas (`vector<pair<latitude, longitude>>`)
- Ordenação in-place (complexidade: O(n log²(n)))
- Método público para range search com 4 parâmetros (limites de latitude e longitude)

#### Como usar a KD-Tree
1. Inicializar com construtor no início do programa
2. Alternativa: Salvar estrutura já montada
3. Para eventos de seleção no mapa:
   - Chamar função C++ passando coordenadas do quadrado
   - Receber resultado em Python (sugestão: lista de tuplas) 