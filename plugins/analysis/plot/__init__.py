import matplotlib.pyplot as plt
import networkx as nx


def plot_graph(graph: nx.Graph, labels=None, node_color=None):
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, node_size=50, cmap=plt.cm.RdYlBu, node_color=node_color, edge_color='gray')
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8)
