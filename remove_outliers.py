import os
import argparse
import numpy as np
from scipy.spatial.distance import cdist
from colmap_python_utils.read_write_model import read_model, write_model
from tqdm import tqdm
from statistics import mean, median, mode, stdev
# from colmap_python_utils.visualize_model import Model

parser = argparse.ArgumentParser(description='')
parser.add_argument('category_index')
args = parser.parse_args()

## Other parameters we can adjust:
##  - Distance treshold(s) for excluding points.
##  - Number of valid points needed to keep an image.

print(f"Importing base model...")
base_model_path = f"base_models/cathedrals/{args.category_index}/sparse/0"
base_cameras, base_images, base_points3D = read_model(base_model_path, ext='.bin')
print(f"Done - {len(base_images)} images  ,  {len(base_points3D)} points")

print(f"Importing extended model...")
extended_model_path = f"extended_models/cathedrals/{args.category_index}/sparse/0"
ext_cameras, ext_images, ext_points3D = read_model(extended_model_path, ext='.bin')
print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

def remove_outlier_points3D(base_points3D, ext_points3D):
    base_points_mat = np.zeros((len(base_points3D), 3))
    i = 0
    missing = 0
    for base_p3d_id in base_points3D:
        if base_p3d_id not in ext_points3D:
            missing += 1
            continue
        base_points_mat[i,:] = ext_points3D[base_p3d_id].xyz
        i += 1

    print(f"missing: {missing}")
    # treshold at 0.005
    new_points3D_0= {}
    # treshold at 0.01
    new_points3D_1= {}
    # treshold at 0.05
    new_points3D_2= {}
    # treshold at 0.3
    new_points3D_3= {}

    ext_p3d_distances = []

    for p3d_id in tqdm(ext_points3D):
        p3d_xyz = ext_points3D[p3d_id].xyz
        dists = np.linalg.norm(base_points_mat - p3d_xyz, axis=1)
        min_dist = np.min(dists)
        ext_p3d_distances.append(min_dist)

        if(min_dist < 0.3):
            new_points3D_3[p3d_id] = ext_points3D[p3d_id]
        if(min_dist < 0.05):
            new_points3D_2[p3d_id] = ext_points3D[p3d_id]
        if(min_dist < 0.01):
            new_points3D_1[p3d_id] = ext_points3D[p3d_id]
        if(min_dist < 0.005):
            new_points3D_0[p3d_id] = ext_points3D[p3d_id]    
        
    # print(f"min: {min(ext_p3d_distances)}")
    # print(f"max: {max(ext_p3d_distances)}")
    # print(f"mean: {mean(ext_p3d_distances)}")
    # print(f"median: {median(ext_p3d_distances)}")
    # print(f"mode: {mode(ext_p3d_distances)}")
    # print(f"std: {stdev(ext_p3d_distances)}")

    print(f"treshold = 0.3: {len(new_points3D_3)}")
    print(f"treshold = 0.05: {len(new_points3D_2)}")
    print(f"treshold = 0.01: {len(new_points3D_1)}")
    print(f"treshold = 0.005: {len(new_points3D_0)}")

    write_model(ext_cameras, ext_images, new_points3D_0, f"extended_models/cathedrals/{args.category_index}/sparse_reduced/0")
    write_model(ext_cameras, ext_images, new_points3D_1, f"extended_models/cathedrals/{args.category_index}/sparse_reduced/1")
    write_model(ext_cameras, ext_images, new_points3D_2, f"extended_models/cathedrals/{args.category_index}/sparse_reduced/2")
    write_model(ext_cameras, ext_images, new_points3D_3, f"extended_models/cathedrals/{args.category_index}/sparse_reduced/3")



print(f"Importing reduced model...")
reduced_model_path = f"extended_models/cathedrals/{args.category_index}/sparse_reduced/2"
reduced_cameras, reduced_images, reduced_points3D = read_model(reduced_model_path, ext='.bin')
print(f"Done - {len(reduced_images)} images  ,  {len(reduced_points3D)} points")

new_images = {}
for img_id in tqdm(reduced_images):
    num_valid_points_in_img = 0
    for p3d_id in reduced_images[img_id].point3D_ids:
        if(p3d_id in reduced_points3D):
            num_valid_points_in_img += 1
        if(num_valid_points_in_img) > 100:
            new_images[img_id] = reduced_images[img_id]
            break

write_model(ext_cameras, new_images, reduced_points3D, f"extended_models/cathedrals/{args.category_index}/sparse_reduced_step2/0")