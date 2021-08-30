# network_analysis_papa

Projeto para a disciplina de Análise de Redes da UFRN ministrada pelo professor  Ivanovitch Silva <https://github.com/ivanovitchm/network_analysis>.
Buscando links da wikipedia a partir da pagina do papa Francisco e assim gerar uma um grafo onde posso descobrir qual é o papa mais citado na wikipedia de acordo com minha rede.

## Pré requisitos

* Python
* PIP
* MongoDB

## Passo a passo

### 1º Instale as bibliotecas necessárias no arquivo requeriments

### 2º Execute com python o arquivo generate_proxies.py para gerar os proxyes retirados do site http://www.freeproxylists.net/
```
python generate_proxies.py
```
### 3º execute com python o arquivo generate_graph.py para o crawler ir varrendo as paginas da wikipedia e ir salvando as citações no mongodb
```
python generate_graph.py
```
### 4º execute com python o arquivo export_graph.py para gerar o arquivo papas.graphml
```
python export_graph.py
```
### Pronto você tem uma rede das paginas wikipedia, agora é apenas tratar esses dados, por exemplo com o Gephi
