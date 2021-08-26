import networkx  as nx
import sys
import pymongo


client = pymongo.MongoClient('mongodb://localhost:27017/')
database = client.get_database('network_analisys')
colection_edges = database.get_collection('papa_edges')

digraph = nx.DiGraph()

edges = list(colection_edges.find({}))
for edge in edges:
    digraph.add_edge(edge['LinkOne'], edge['LinkTwo'])

print('Número de edges', digraph.number_of_edges())

dioriginal = digraph.copy()
digraph.remove_edges_from(nx.selfloop_edges(digraph))

# filter nodes with degree greater than or equal to 2
core = [node for node, deg in dict(digraph.degree()).items() if deg >= 2]

# select a subgraph with 'core' nodes
gsub = nx.subgraph(digraph, core)

print("{} nodes, {} edges".format(len(gsub), nx.number_of_edges(gsub)))

nx.write_graphml(gsub, "papas.graphml")

sys.exit()