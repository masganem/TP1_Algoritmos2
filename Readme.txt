O que foi feito até agora:

O location_data_parser puxa os dados dos estabelecimentos da prefeitura, limpa eles para manter apenas os restaurantes
e bares, e usa a api do OpenStreetView para puxar as coordenadas geograficas à partir do endereço. Isso é feito com
o dataframe useful_bars_dataset, que não possui todos os dados necessários. O motivo disso é que o formato do endereço 
usado para puxar as coordenadas omite alguns detalhes que poderiam atrapalhar a API, como complemento, andar etc. 
Logo, temos que cruzar a tabela useful_bars_dataset com a tabela final_bars_and_restaurants, e dropar a coluna useful_address

Eu já rodei a função que puxa as coordenadas, o output dela ta em geocoded_bars_and_restaurantes.csv. Entretanto, eu consegui
ver vários restaurantes e bares que não foi possível puxar as coordenadas, não imagino que isso seja um problema tão grande,
a maioria das linhas do csv tem as coordenadas, mas é importante ressaltar isso.

Ainda temos que cruzar com os dados do comida de buteco. O Vimieiro falou que pode ser um problema cruzar, pq no site do comida
de boteco os nomes estão escritos de forma diferente do que os registrados na prefeitura. A solução que eu sugiro fazermos é 
baixar o csv com os nomes de todos os bares do comida di buteco, usarmos novamente a api do OpenStreetView (pq ela nao tem tanto
problema com nomes escritos errado) e depois damos um join com a nossa tabela antiga, à partir da coordenada. Ai criamos uma coluna
com apenas um booleano indicando se é ou não parte do comida di buteco. Coisa bem simples de se fazer imagino.

Por último, scratch.cpp tem a implementação da kd tree, e da função do range search. A forma como ela é implementada é, ela tem um construtor,
que recebe uma lista de coordenadas (vector<pair<latitude, longitude>>) (latitude e longitude é so um alias pra float) e já ordena a kdtree inplace
(eu fiz de um jeito um pouco diferente, mas segundo as minhas contas, a complexidade é ainda O(n log^2(n))), que parece razoavelmente aceitavel.
Para executar o range search basta usar o método publico da classe Kd-tree passando 4 valores, os limites de latitude e os de longitude.
A forma como eu recomendo que vc faça isso é no início do seu programa vc chama o construtor da kd-tree e coloca os dados, ou também nos podemos
salvar ela ja montada e chamar com uma função qualquer. O motivo disso é que é mais rapido mexer com coisa ja carregada na memoria (nao é tanta Coisa
assim entao acho que da) ai toda vez que tiver um evento de alguem desenhar um quadrado no mapa vc chama a função em c++ e passa as coordenadas do 
quadrado pra função e puxa de volta o resultado no tipo que vc tiver definido em python(nao sei qual é, mas imagino que uma lista de tuplas faça sentido)

Por enquanto é isso.