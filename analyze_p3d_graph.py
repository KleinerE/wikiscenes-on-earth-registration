import argparse
import numpy as np
import json
import networkx as nx
from tqdm import tqdm
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='construct indexes for comparing extended model to reference models.')
parser.add_argument('category_index')
args = parser.parse_args()

reference_path_base = f"reference_models/cathedrals/{args.category_index}"

with open(f"{reference_path_base}/points3d_graph.json", "r") as infile:
    universal_point3d_graph = json.load(infile)


## Approach 1: Pointers Dict. ##
# Each Point3D has a its own dictionary.
# In there, for each other model (component), we store only the best-matching Point3D. (one with the most amount of pointers).
# In case a Point3D points at the same weight to multiple other Point3D's (of the same other model), we choose not to choose. The point does not enter the pointers dict.

universal_point3d_pointers = {}

def add_pair_to_pointers_dict(component_idx_1, point3D_id_1, component_idx_2, point3D_id_2):
    if component_idx_1 not in universal_point3d_pointers:
        universal_point3d_pointers[component_idx_1] = {}

    if point3D_id_1 not in universal_point3d_pointers[component_idx_1]:
        universal_point3d_pointers[component_idx_1][point3D_id_1] = {}

    if component_idx_2 not in universal_point3d_pointers[component_idx_1][point3D_id_1]:
        universal_point3d_pointers[component_idx_1][point3D_id_1][component_idx_2] = point3D_id_2
    else:
        print("ALREADY TAKEN") # should never happen


for component_idx in universal_point3d_graph:
    for p3d_id in universal_point3d_graph[component_idx]:
        for other_component_idx in universal_point3d_graph[component_idx][p3d_id]:
            other_points3d = universal_point3d_graph[component_idx][p3d_id][other_component_idx]
            srt = sorted(other_points3d, key=other_points3d.get)
            if(len(srt) == 1 or other_points3d[srt[-1]] > other_points3d[srt[-2]]):
                matching_pt = srt[-1]
                add_pair_to_pointers_dict(component_idx, p3d_id, other_component_idx, matching_pt)
            elif len(srt) > 1:
                print(other_component_idx, srt[-1], srt[-2])

exit()

# Optional 2nd pass - pick up undecided points.
# for component_idx in universal_point3d_graph:
#     for p3d_id in universal_point3d_graph[component_idx]:
#         for other_component_idx in universal_point3d_graph[component_idx][p3d_id]:      
#             if p3d_id not in universal_point3d_pointers[component_idx] or other_component_idx not in universal_point3d_pointers[component_idx][p3d_id]: # this point has not decided in the first pass.    
#                 other_points3d = universal_point3d_graph[component_idx][p3d_id][other_component_idx]
#                 for other_p3d_id in other_points3d:
#                     if other_component_idx in universal_point3d_pointers \
#                                 and other_p3d_id in universal_point3d_pointers[other_component_idx] \
#                                 and component_idx in universal_point3d_pointers[other_component_idx][other_p3d_id]:
#                         if universal_point3d_pointers[other_component_idx][other_p3d_id][component_idx] == p3d_id:
#                             add_pair_to_pointers_dict(component_idx, p3d_id, other_component_idx, other_p3d_id)

# point3d_distilled_graph_path = f"{reference_path_base}/points3d_graph_d.json"
# with open(point3d_distilled_graph_path, "w") as outfile:
#     json.dump(universal_point3d_pointers, outfile)
#     print(f"wrote points3D graph to {point3d_distilled_graph_path}")

## Analyze rate of matching points ##
missing_target_point = 0
missing_component_back = 0
other_point3d_back = 0
valid_points = 0
universal_point3D_pairs = {}

def check_pair_exists(component_idx_1, point3D_id_1, component_idx_2, point3D_id_2):
    for c1, p1, c2, p2 in universal_point3D_pairs:
        if component_idx_2 == c1 and point3D_id_2 == p1 and component_idx_1 == c2 and point3D_id_1 == p2:
            return True
    return False

for component_idx_1 in universal_point3d_pointers:
    for point3D_id_1 in universal_point3d_pointers[component_idx_1]:
        for component_idx_2 in universal_point3d_pointers[component_idx_1][point3D_id_1]:            
            point3D_id_2 = universal_point3d_pointers[component_idx_1][point3D_id_1][component_idx_2]
            if point3D_id_2 not in universal_point3d_pointers[component_idx_2]:
                missing_target_point += 1
            else:
                if component_idx_1 not in universal_point3d_pointers[component_idx_2][point3D_id_2]:
                    missing_component_back += 1                    
                else:
                    point3D_id_2_back = universal_point3d_pointers[component_idx_2][point3D_id_2][component_idx_1]
                    if point3D_id_2_back != point3D_id_1:
                        other_point3d_back += 1
                    else:
                        valid_points += 1
                        if f"{component_idx_2}:{point3D_id_2}" not in universal_point3D_pairs: # the reverse pair already exists - do not enter the same pair again.
                            universal_point3D_pairs[f"{component_idx_1}:{point3D_id_1}"] = f"{component_idx_2}:{point3D_id_2}"

print(valid_points)
print(missing_target_point)
print(missing_component_back)
print(other_point3d_back)


# pairs_path = f"{reference_path_base}/points3d_pairs.json"
# with open(pairs_path, "w") as outfile:
#     json.dump(universal_point3D_pairs, outfile)
#     print(f"wrote points3D graph to {pairs_path}")

G = nx.Graph()

for key in universal_point3D_pairs:
    G.add_edge(key, universal_point3D_pairs[key])

# for component_idx_1 in universal_point3d_pointers:
#     for point3D_id_1 in universal_point3d_pointers[component_idx_1]:
#         start_node_name = f"{component_idx_1}:{point3D_id_1}"
#         for component_idx_2 in universal_point3d_pointers[component_idx_1][point3D_id_1]:
#             point3D_id_2 = universal_point3d_pointers[component_idx_1][point3D_id_1][component_idx_2]
#             end_node_name = f"{component_idx_2}:{point3D_id_2}"
#             # print(end_node_name)
#             G.add_edge(start_node_name, end_node_name)

print(nx.number_connected_components(G))

lens = {}
invalid_ccs = 0
for c in nx.connected_components(G):
    l = len(c)
    if l not in lens:
        lens[l] = 0
    lens[l] += 1
    if l >= 5:
        print(c)
    # components = [int(n.split(':')[0]) for n in c]
    # if(len(set(components)) != len(components)):
    #     invalid_ccs += 1
    
print(lens)

print(invalid_ccs)
exit()
G = nx.Graph()

for component_idx in universal_point3d_graph:
    for p3d_id in universal_point3d_graph[component_idx]:
        for other_component_idx in universal_point3d_graph[component_idx][p3d_id]:
            other_points3d = universal_point3d_graph[component_idx][p3d_id][other_component_idx]
            # matching_pt = max(other_points3d, key=other_points3d.get)
            start_node_name = f"{component_idx}:{p3d_id}"
            for other_p3d in other_points3d:
                end_node_name = f"{other_component_idx}:{other_p3d}"
                G.add_edge(start_node_name, end_node_name, weight=other_points3d[other_p3d])

# print(G.number_of_nodes())
# print(G.number_of_edges())

# cliques = list(nx.enumerate_all_cliques(G))
# print(len(cliques))

# for C in nx.enumerate_all_cliques(G):
#     print(C)
#     exit()

for N in G.nodes:
    node_edges=sorted(G.edges(data=True), key=lambda t: t[2].get('weight', 1))
    print(G[N])
    exit()
# for N in G.adj['0:244035']:
    # print(N)

# edges=sorted(G.edges(data=True), key=lambda t: t[2].get('weight', 1))
# print(edges[-20:])


# pos = nx.spring_layout(G, seed=7)

# # nodes
# nx.draw_networkx_nodes(G, pos, node_size=7)

# # edges
# nx.draw_networkx_edges(G, pos, width=6)

# # node labels
# nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
# # edge weight labels
# edge_labels = nx.get_edge_attributes(G, "weight")
# nx.draw_networkx_edge_labels(G, pos, edge_labels)

# ax = plt.gca()
# ax.margins(0.08)
# plt.axis("off")
# plt.tight_layout()
# plt.show()