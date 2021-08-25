from random import randint
import networkx  as nx
import matplotlib.pyplot as plt
import time
import sys
import threading
import requests
import queue
import re
import json
import pymongo


client = pymongo.MongoClient('mongodb://localhost:27017/')
database = client.get_database('network_analisys')
colection_papa = database.get_collection('papa_network')
colection_visited = database.get_collection('visited_links')
queue_links = queue.Queue()
proxies = json.load(open('proxies.json'))

#Get links of https://pt.wikipedia.org/wiki/Papa_Francisco
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}
r_inicial = requests.get(
    'https://pt.wikipedia.org/wiki/Papa_Francisco', 
    headers=headers)

response_raw = re.search(r'mw-content-text.*?catlinks', r_inicial.text, flags=re.DOTALL).group()
regex_links = re.findall(
    r'<a\s+href="/wiki/[^"]+"\s+title="(?P<title>[^"]+)">[^<]+</a>',
    response_raw, flags=re.DOTALL|re.IGNORECASE
)

for link in regex_links:
    regex = r'papa|clero|cardea|roma|são|credo|culto|vaticano|bispo'
    if re.search(regex, link, flags=re.IGNORECASE) is not None:
        queue_links.put({'Link': link, 'Layer': 1})        
        colection_papa.update(
            {'LinkOne': 'Papa Francisco', 'LinkTwo': link}, 
            {'$set': {'LinkOne': 'Papa Francisco', 'LinkTwo': link}}, 
            upsert=True
        )
    
print('Links encontrados - ', queue_links.qsize())
def get_links(colection_papa, colection_visited, proxie_dic):    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    
    while not queue_links.empty():
        obj = queue_links.get()   
        print('Tamanho da pilha:', queue_links.qsize())                                   
        link_dad = obj['Link']
        layer = obj['Layer']
        print(f'Salvando dados do link {link_dad} - Layer: {layer}')
        url = 'https://pt.wikipedia.org/wiki/' + link_dad.replace(' ', '_')        
        try:
            r_inicial = requests.get(
                url, proxies=proxie_dic,
                headers=headers
            )

            colection_visited.update(
                {'Link': link_dad}, 
                {'$set': {'Link': link_dad}}, 
                upsert=True
            )

            response_raw = re.search(r'mw-content-text.*?catlinks', r_inicial.text, flags=re.DOTALL).group()
            regex_links = re.findall(
                r'<a\s+href="/wiki/[^"]+"\s+title="(?P<title>[^"]+)">[^<]+</a>',
                response_raw, flags=re.DOTALL|re.IGNORECASE
            )
            for link in regex_links:
                regex = r'papa|clero|cardea|roma|são|credo|culto|vaticano|bispo'                
                
                if re.search(regex, link, flags=re.IGNORECASE) is not None:
                    colection_papa.update(
                        {'LinkOne': link_dad, 'LinkTwo': link}, 
                        {'$set': {'LinkOne': link_dad, 'LinkTwo': link}}, 
                        upsert=True
                    )
                    visited_link = colection_visited.find_one({'Link': link})
                    if visited_link is None and layer < 3:
                        queue_links.put({'Link': link, 'Layer': layer+1})            
                        
        except Exception:
            pass
    
        queue_links.task_done()    
    

print(len(proxies), 'proxies encontrados')
for proxie in proxies:
    proxie_dic = {
        'https': f'http://{proxie["ip"]}:{proxie["porta"]}'
    }

    print(f'Iniciando Thread {proxie["ip"]}..')
    process_thread = threading.Thread(target=get_links, args=(colection_papa, colection_visited, proxie_dic))
    process_thread.daemon = True
    process_thread.start()

queue_links.join()
client.close()
print('Links concluidos !!!')

# digraph = nx.DiGraph()
# print('Número de edges', digraph.number_of_edges())

# dioriginal = digraph.copy()
# digraph.remove_edges_from(nx.selfloop_edges(digraph))

# # filter nodes with degree greater than or equal to 2
# core = [node for node, deg in dict(digraph.degree()).items() if deg >= 2]

# # select a subgraph with 'core' nodes
# gsub = nx.subgraph(digraph, core)

# print("{} nodes, {} edges".format(len(gsub), nx.number_of_edges(gsub)))

# nx.write_graphml(gsub, "papas.graphml")

sys.exit()