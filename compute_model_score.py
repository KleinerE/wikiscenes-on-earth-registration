import os
import argparse
import numpy as np
from tqdm import tqdm
from colmap_python_utils.read_write_model import read_model

parser = argparse.ArgumentParser(description='Computes extended model score based on reference model')
parser.add_argument('category_index')
args = parser.parse_args()

reference_model_path_base = f"reference_models/cathedrals/{args.category_index}/sparse"
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

print("Analyzing...")

# Go over all images in extended model. for each one, find if it's in any of the reference models.
img_ref_component_idxs = np.ones((len(ext_images))) * -1
i = 0
for ext_img in tqdm(ext_images):
    img_name = ext_images[ext_img].name
    for component_idx, ref_cameras, ref_images, ref_points3D in ref_models:
        for ref_img in ref_images:
            if(ref_images[ref_img].name == img_name):
                img_ref_component_idxs[i] = component_idx
                break             
    i += 1

print(f"Previously unregistered images: {(img_ref_component_idxs == -1).sum()}")
for i in range(len(ref_models)):
    print(f"Previously registered in component #{i} -> {(img_ref_component_idxs == i).sum()}")

# Go over all images in the reference models. for each one, find if it's in the extended model. if not, it's considered a 'lost' image.
nonlost_images_count = 0
for component_idx, ref_cameras, ref_images, ref_points3D in ref_models:
    for ref_img in ref_images:
        for ext_img in ext_images:
            if(ref_images[ref_img].name == ext_images[ext_img].name):
                nonlost_images_count += 1
                break


print(f"Lost images: {len(ext_images) - nonlost_images_count}")

#TODO analyze points.