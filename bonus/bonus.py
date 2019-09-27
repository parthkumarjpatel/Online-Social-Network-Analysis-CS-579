import networkx as nx

def jaccard_wt(graph, node):
    """
    The weighted jaccard score, defined in bonus.md.
    Args:
      graph....a networkx graph
      node.....a node to score potential new edges for.
    Returns:
      A list of ((node, ni), score) tuples, representing the 
                score assigned to edge (node, ni)
                (note the edge order)
    """
    ###TODO
    JaccardScore=[]
    ListDegree = [graph.degree(a) for a in graph.neighbors(node)]
    NeighborCount1 = sum(ListDegree)
    
    for TempNode in graph.nodes():
        if TempNode == node or (graph.has_edge(node, TempNode)):
            continue
        else:
            CommonNode = (set(graph.neighbors(node)) & set(graph.neighbors(TempNode)))
            
            ListDegree2 = [graph.degree(a) for a in graph.neighbors(TempNode)]
            NeighborCount2 = sum(ListDegree2)
            
            denominator = float(1/NeighborCount1) + float(1/NeighborCount2)
            #print(denominator,TempNode)
            
            CommonNodeCount=0
            for EachNode in CommonNode:
                CommonNodeCount += float(1/graph.degree(EachNode))
            #print(denominator)
            
            score = float(CommonNodeCount/denominator)
            JaccardScore.append(((node,TempNode),score))
    return sorted(JaccardScore, key=lambda x: x[-1:], reverse=True)[:]