from app import models
import networkx as nx


def create_journal_graph(entries: models.Journal):
    G = nx.Graph(())
    """Create a graph of the journal entries"""
    links = {}
    for i in range(len(entries)):
        G.add_node(entries[i].id)
        links.update({entries[i].id: entries[i].link_ids})

    for key in links:
        value = links[key]
        if value is not None:
            for value in links[key]:
                G.add_edge(key, value)

    return list(G.nodes), list(G.edges)
