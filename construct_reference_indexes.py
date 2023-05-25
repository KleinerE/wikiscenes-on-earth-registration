import os
import argparse
import numpy as np
import networkx as nx
import json
from tqdm import tqdm
from colmap_python_utils.read_write_model import read_model

parser = argparse.ArgumentParser(description='construct indexes for comparing extended model to reference models.')
parser.add_argument('category_index')
args = parser.parse_args()

reference_path_base = f"reference_models/cathedrals/{args.category_index}"
reference_model_path_base = f"{reference_path_base}/sparse"
ref_models = []
list_subfolders_with_paths = [f.path for f in os.scandir(reference_model_path_base) if f.is_dir()]
print(f"reference model has {len(list_subfolders_with_paths)} components. Importing...")
for i in range(len(list_subfolders_with_paths)): 
    submodel_dir = list_subfolders_with_paths[i]
    ref_cameras, ref_images, ref_points3D = read_model(submodel_dir, ext='.bin')
    print(f"#{i} -> {len(ref_images)} images  ,  {len(ref_points3D)} points")
    ref_models.append((i, ref_cameras, ref_images, ref_points3D))
print("Done.")

print(f"Importing extended model...")
extended_model_path = f"extended_models/cathedrals/{args.category_index}/sparse/0"
ext_cameras, ext_images, ext_points3D = read_model(extended_model_path, ext='.bin')
print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

# ## Images Index ##

# def construct_images_index(ref_models, ext_cameras, ext_images, ext_points3D):
#     # Extended image ID to reference model + image ID
#     # Go over all images in extended model. for each one, find if it's in any of the reference models.
#     universal_images_index = {}
#     for ext_img in ext_images:
#         img_name = ext_images[ext_img].name
#         universal_images_index[img_name] = {-1: ext_img}

#     # Reference model + image ID to extended image ID.
#     # we do this to detect how much data was lost during our extended reconstruction.
#     # Go over all images in the reference models. for each one, find if it's in the extended model. if not, it's considered a 'lost' image.
#     for component_idx, ref_cameras, ref_images, ref_points3D in ref_models:
#         for ref_img in ref_images:
#             img_name = ref_images[ref_img].name
#             if img_name not in universal_images_index:
#                 universal_images_index[img_name] = {}
#             universal_images_index[img_name][component_idx] = ref_img

#     return universal_images_index

## Point2D Index ##
overwrites = {}
def construct_point2d_index(ref_models, ext_cameras, ext_images, ext_points3D):
    universal_point2d_index = {}
    # for ext_p3d_id in ext_points3D:
    #     ext_points2d = zip(ext_points3D[ext_p3d_id].image_ids, ext_points3D[ext_p3d_id].point2D_idxs)
    #     for ext_img_id, ext_p2d_idx in ext_points2d:
    #         img_name = ext_images[ext_img_id].name
    #         if img_name not in universal_point2d_index:
    #             universal_point2d_index[img_name] = {}
    #         if int(ext_p2d_idx) in universal_point2d_index[img_name]:
    #             if -1 in universal_point2d_index[img_name][int(ext_p2d_idx)]:
    #                 print("OVERWRITE")
    #         universal_point2d_index[img_name][int(ext_p2d_idx)] = {-1: ext_p3d_id}


    for component_idx, ref_cameras, ref_images, ref_points3D in ref_models:
        for ref_p3d_id in ref_points3D:
            ref_points2d = zip(ref_points3D[ref_p3d_id].image_ids, ref_points3D[ref_p3d_id].point2D_idxs)
            for ref_img_id, ref_p2d_idx in ref_points2d:
                img_name = ref_images[ref_img_id].name
                if img_name not in universal_point2d_index:
                    universal_point2d_index[img_name] = {}
                if int(ref_p2d_idx) not in universal_point2d_index[img_name]:
                    universal_point2d_index[img_name][int(ref_p2d_idx)] = {}
                if component_idx in universal_point2d_index[img_name][int(ref_p2d_idx)]:
                    if component_idx not in overwrites:
                        overwrites[component_idx] = 0
                    overwrites[component_idx] += 1
                universal_point2d_index[img_name][int(ref_p2d_idx)][component_idx] = ref_p3d_id

    print(f"overwrites: {overwrites}")
    return universal_point2d_index
    # point2d_index_path = f"{reference_path_base}/points2d_index.json"
    # with open(point2d_index_path, "w") as outfile:
    #     json.dump(universal_point2d_index, outfile)
    #     print(f"wrote points2D index to {point2d_index_path}")


# with open(f"{reference_path_base}/points2d_index.json", "r") as infile:
#     universal_point2d_index = json.load(infile)



## Point3D Graph ##

def construct_point3d_graph(universal_point2d_index, ref_models, ext_cameras, ext_images, ext_points3D):

    # universal_point3d_graph = {-1: {}}
    # for ext_p3d_id in ext_points3D:
    #     ext_points2d = zip(ext_points3D[ext_p3d_id].image_ids, ext_points3D[ext_p3d_id].point2D_idxs)
    #     for ext_img_id, ext_p2d_idx in ext_points2d:
    #         img_name = ext_images[ext_img_id].name
    #         for point3d_component_idx in universal_point2d_index[img_name][int(ext_p2d_idx)]:
    #             if int(point3d_component_idx) != -1 :
    #                 if ext_p3d_id not in universal_point3d_graph[-1]:
    #                     universal_point3d_graph[-1][ext_p3d_id] = {}

    #                 if point3d_component_idx not in universal_point3d_graph[-1][ext_p3d_id]:
    #                     universal_point3d_graph[-1][ext_p3d_id][point3d_component_idx] = {}

    #                 other_p3d_id = universal_point2d_index[img_name][int(ext_p2d_idx)][point3d_component_idx]

    #                 if other_p3d_id not in universal_point3d_graph[-1][ext_p3d_id][point3d_component_idx]:
    #                     universal_point3d_graph[-1][ext_p3d_id][point3d_component_idx][other_p3d_id] = 0

    #                 universal_point3d_graph[-1][ext_p3d_id][point3d_component_idx][other_p3d_id] += 1
    universal_point3d_graph = {}
    for component_idx, ref_cameras, ref_images, ref_points3D in ref_models:
        for ref_p3d_id in ref_points3D:
            ref_points2d = zip(ref_points3D[ref_p3d_id].image_ids, ref_points3D[ref_p3d_id].point2D_idxs)
            for ref_img_id, ref_p2d_idx in ref_points2d:
                img_name = ref_images[ref_img_id].name
                for point3d_component_idx in universal_point2d_index[img_name][int(ref_p2d_idx)]:
                    if int(point3d_component_idx) != component_idx :

                        if component_idx not in universal_point3d_graph:
                            universal_point3d_graph[component_idx] = {}

                        if ref_p3d_id not in universal_point3d_graph[component_idx]:
                            universal_point3d_graph[component_idx][ref_p3d_id] = {}

                        if point3d_component_idx not in universal_point3d_graph[component_idx][ref_p3d_id]:
                            universal_point3d_graph[component_idx][ref_p3d_id][point3d_component_idx] = {}

                        other_p3d_id = universal_point2d_index[img_name][int(ref_p2d_idx)][point3d_component_idx]

                        if other_p3d_id not in universal_point3d_graph[component_idx][ref_p3d_id][point3d_component_idx]:
                            universal_point3d_graph[component_idx][ref_p3d_id][point3d_component_idx][other_p3d_id] = 0

                        universal_point3d_graph[component_idx][ref_p3d_id][point3d_component_idx][other_p3d_id] += 1

    return universal_point3d_graph
    # point3d_graph_path = f"{reference_path_base}/points3d_graph.json"
    # with open(point3d_graph_path, "w") as outfile:
    #     json.dump(universal_point3d_graph, outfile)
    #     print(f"wrote points3D graph to {point3d_graph_path}")



# with open(f"{reference_path_base}/points3d_graph.json", "r") as infile:
#     universal_point3d_graph = json.load(infile)


### Point3D Groups ###

def construct_point3D_groups(universal_point3d_graph, show_stats=False):

    ## Step 1: Pointers Dict. ##
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

    def count_groups_containing_model(point_groups, model_num):
        i=0
        for g in point_groups:
            for n in g:
                if int(n.split(":")[0]) == model_num:
                    i += 1
                    break
        return i

    for component_idx in universal_point3d_graph:
        for p3d_id in universal_point3d_graph[component_idx]:
            for other_component_idx in universal_point3d_graph[component_idx][p3d_id]:
                other_points3d = universal_point3d_graph[component_idx][p3d_id][other_component_idx]
                srt = sorted(other_points3d, key=other_points3d.get)
                if(len(srt) == 1 or other_points3d[srt[-1]] > other_points3d[srt[-2]]):
                    matching_pt = srt[-1]
                    add_pair_to_pointers_dict(component_idx, p3d_id, other_component_idx, matching_pt)


    ## Step 2 : Cleanup Pairs ##
    missing_target_point = 0
    missing_component_back = 0
    other_point3d_back = 0
    valid_points = 0
    universal_point3D_pairs = {}

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

    if(show_stats):
        print("\n##################      PAIR CLEANUP STATS      ##################")
        print(f"Target point has ambiguity: {missing_target_point}")
        print(f"Target point missing source model: {missing_component_back}")
        print(f"Target point points back to different source point: {other_point3d_back}")
        print(f"# VALID POINTS : {int(valid_points/2)} #")
        print("##################################################################")


    ## Step 3 : Point Groups ##
    G = nx.Graph()

    for key in universal_point3D_pairs:
        G.add_edge(key, universal_point3D_pairs[key])

    point_groups = list(nx.connected_components(G))

    if(show_stats):
        groups_containing_extended = 0
        num_groups_containing_each_ref_model = {}
        for g in point_groups:
            for n in g:
                if int(n.split(":")[0]) == -1:
                    groups_containing_extended += 1
                    break

        print("\n##################      POINT GROUP STATS      ##################")
        print(f"Total number of groups: {len(point_groups)}")
        print(f"Groups containing the extended model: {count_groups_containing_model(point_groups, -1)}")
        for model_num in range(len(ref_models)):
            print(f"Groups containing model #{model_num}: {count_groups_containing_model(point_groups, model_num)}")
        print("##################################################################")
    return point_groups



print("Constructing Point2D Index...")
universal_point2d_index = construct_point2d_index(ref_models, ext_cameras, ext_images, ext_points3D)
print("Done.")

print("Constructing Point3D Graph...")
universal_point3d_graph = construct_point3d_graph(universal_point2d_index, ref_models, ext_cameras, ext_images, ext_points3D)
print("Done.")

print("Refining Point3D Groups...")
point3d_groups = construct_point3D_groups(universal_point3d_graph, show_stats=True)
print("Done.")
print(f"Point3D groups found: {len(point3d_groups)}")

point3d_groups_path = f"{reference_path_base}/points3d_groups_aaa.json"
with open(point3d_groups_path, "w") as outfile:
    outfile.write("\n".join(",".join(s for s in group) for group in point3d_groups))
    print(f"Wrote points3D groups to {point3d_groups_path}")