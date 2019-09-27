#Assignment-4 
#A20416508 - Parthkumar Patel
#Perform community detection to cluster users into communities.
"""
Cluster data.
"""
import json
from collections import Counter, defaultdict, deque
import copy
import networkx as nx
import re
import itertools
import matplotlib.pyplot as plt


def readData():
    """ reads the data collected in the 'collect.py'
    Return:
        a json object with tweetsdata.
    """
    return json.loads(open('collectTweetResult.json').read())

def buildGraph(tweetsdata):
    """ use tweetsdata to build a graph with @ users
    Params:
        tweetsdata ... a json object with tweetsdata.
    Return:
        graph .... a networkx graph with user @ edges.
    """
    graph = nx.Graph()
    for eachtweet in tweetsdata:
        if '@' in eachtweet['text']:
            mentioneduser = re.findall(r'[@]\S+', eachtweet['text']) #find all mentioned user in the tweets
            #Create a networkx undirected Graph, adding each screenname and mentioned user as a node
            for mention in mentioneduser:
                graph.add_node(eachtweet['user']['screen_name']) #get screen name of user as a node
                graph.add_node(mention[1:]) # add mentioned user as a node
                graph.add_edge(eachtweet['user']['screen_name'], mention[1:]) #add a edge between user's screenname and mentioned user
    return graph

def draw_network(graph):
    """
    Draw the network to a file.
    """
    plt.figure(figsize=(12,12))
    nx.draw_networkx(graph,pos=nx.spring_layout(graph),alpha=.5, with_labels=False,width=.5, node_size=100,node_color='blue',edge_color='green')
    plt.axis("off")
    plt.savefig("graphwithoutlabel.png")
    print("\nGraph without label is saved in graphwithoutlabel.png")

    plt.figure(figsize=(12,12))
    nx.draw_networkx(graph,pos=nx.spring_layout(graph),alpha=.5, with_labels=True,width=.5, node_size=100,node_color='blue',edge_color='green')
    plt.axis("off")
    plt.savefig("graphwithlabel.png")
    print("\nGraph with label is saved in graphwithlabel.png")

def bfs(graph, root, max_depth):
    """
    Perform breadth-first search to compute the shortest paths from a root node to all
    other nodes in the graph. To reduce running time, the max_depth parameter ends
    the search after the specified depth.
    E.g., if max_depth=2, only paths of length 2 or less will be considered.
    This means that nodes greather than max_depth distance from the root will not
    appear in the result.
    Params:
      graph.......A networkx Graph
      root........The root node in the search graph (a string). We are computing
                  shortest paths from this node to all others.
      max_depth...An integer representing the maximum depth to search.

    Returns:
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node that pass through this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree
    """
    q = deque()
    q.append(root)
    seen = set()
    seen.add(root)
    node2distances = defaultdict(int)
    node2num_paths = defaultdict(int)
    node2num_paths[root] = 1
    node2parents = defaultdict(list)
    #recursive BFS
    while q:
        n = q.popleft()
        #jump out when one search reach the max_depth
        if node2distances[n] == max_depth:
            continue
        for nn in graph.neighbors(n):
            if nn not in seen:
                q.append(nn)
                node2distances[nn] = node2distances[n] + 1
                node2num_paths[nn] = node2num_paths[n]
                node2parents[nn].append(n)
                seen.add(nn)
            elif node2distances[nn] == node2distances[n] + 1:
                node2parents[nn].append(n)
                node2num_paths[nn] += node2num_paths[n]
    return node2distances, node2num_paths, node2parents

def bottom_up(root, node2distances, node2num_paths, node2parents):
    """
    Compute the final step of the Girvan-Newman algorithm.
    Params:
      root.............The root node in the search graph (a string). We are computing
                       shortest paths from this node to all others.
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node that pass through this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree
    Returns:
      A dict mapping edges to credit value. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).

      Any edges excluded from the results in bfs should also be exluded here.
    """
    node2credit_value = defaultdict(int)
    edge2credit_value = defaultdict(int)
    sorted_nodes = sorted(node2distances.items(), key = lambda x:x[1], reverse = True)
    
    #Each node otherthan the root is given credict 1
    node2credit_value[root] = 0
    for n,d in sorted_nodes:
        if n != root:
            node2credit_value[n] = 1
    #bottom up
    for n,d in sorted_nodes:
        #sum the path to node
        path2node = 0
        for p in node2parents[n]:
            path2node += node2num_paths[p]
        #bottom up the node credit to edge credit
        for p in node2parents[n]:
            edge = tuple(sorted((n, p)))
            edge2credit_value[edge] = node2credit_value[n] * node2num_paths[p] / path2node
            node2credit_value[p] += edge2credit_value[edge]
    return edge2credit_value

def approximate_betweenness(graph, max_depth):
    """
    Compute the approximate betweenness of each edge, using max_depth to reduce
    computation time in breadth-first search.
    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.

    Returns:
      A dict mapping edges to betweenness. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).
    """
    edge2betweenness = defaultdict(int)
    for n in graph.nodes():
        node2distances, node2num_paths, node2parents = bfs(graph, n, max_depth)
        edge2credit_value = bottom_up(n, node2distances, node2num_paths, node2parents)
        for e,c in edge2credit_value.items():
            edge2betweenness[tuple(sorted(e))] += c
    # divide by 2
    for e,c in edge2credit_value.items():
        edge2betweenness[e] = c / 2
    return edge2betweenness

def partition_girvan_newman(graph, max_depth):
    """
    Use your approximate_betweenness implementation to partition a graph.
    Unlike in class, here you will not implement this recursively. Instead,
    just remove edges until more than one component is created, then return
    those components.
    That is, compute the approximate betweenness of all edges, and remove
    them until multiple comonents are created.
    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.

    Returns:
      A list of networkx Graph objects, one per partition.
    """
    copy = graph.copy()
    betweenness = sorted(approximate_betweenness(copy, max_depth).items(), key= lambda x: (-x[1],x[0][0],x[0][1]))
    for edge,val in betweenness:
        copy.remove_edge(*edge)
        if nx.number_connected_components(copy) > 1:
            break
    partition_graph = sorted(list(nx.connected_component_subgraphs(copy)), key = lambda x: -len(x))
    return partition_graph

def main():
    tweetsdata = readData() #reads tweet data
    graph = buildGraph(tweetsdata) #build a graph 
    draw_network(graph) #draw a graph
    clusters = partition_girvan_newman(graph, 5) # performed partition girwan newman algorithm for community detection

    communityCluster = [] #array to store cluster's node 
    for i in range(len(clusters)):
        communityCluster.append(str(clusters[i].nodes())) #append each cluster's node into list
    
    filename = 'clusteredData.json'
    with open(filename, 'w', encoding = 'utf-8') as outputfile:
        json.dump(communityCluster,outputfile,indent=4)
    print("\nCompleted data clustering.\n\nClustered data stored in 'clusteredData.json'.\n")

if __name__ == '__main__':
    main()
