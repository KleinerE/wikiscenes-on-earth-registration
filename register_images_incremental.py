import os
import shutil
import subprocess
import argparse
import datetime
import json
import numpy as np
from tqdm import tqdm
from colmap_python_utils.read_write_model import read_model

def register_image(original_model_path, candidates_model_path, database_path, images_path, image_name):
    # Create 'image list' file
    imagelist = f"{original_model_path}\imagelist.txt"
    with open(imagelist, 'w') as f:
        f.write(image_name)    
    
    colmap_path = r"C:\Projects\Uni\COLMAP-3.7-windows-cuda\COLMAP.bat"
    # Run feature extractor
    print(f"[{datetime.datetime.now().time()}] {image_name}: extracting features...")
    subprocess.run([colmap_path, "feature_extractor",
                    "--database_path", database_path,
                    "--image_path", images_path,
                    "--image_list_path", imagelist], stdout=subprocess.DEVNULL)
    # Run exhaustive matcher
    print(f"[{datetime.datetime.now().time()}] {image_name}: matching features...")
    subprocess.run([colmap_path, "exhaustive_matcher",
                    "--database_path", database_path,
                    "--SiftMatching.min_num_inliers", str(5)], stdout=subprocess.DEVNULL)
    # Run mapper
    print(f"[{datetime.datetime.now().time()}] {image_name}: mapping...")
    subprocess.run([colmap_path, "mapper",
                    "--database_path", database_path,
                    "--image_path", images_path,
                    "--input_path", original_model_path,
                    "--output_path", candidates_model_path], stdout=subprocess.DEVNULL)
    return



def test_image_reconstruction(model_path, base_model_path, image_name, distance_treshold):
    # Load models
    base_cameras, base_images, base_points3D = read_model(base_model_path, ext='.bin')
    ext_cameras, ext_images, ext_points3D = read_model(model_path, ext='.bin')
    
    # Construct matrix of base points coordinates
    base_points_mat = np.zeros((len(base_points3D), 3))
    i = 0
    missing = 0
    for base_p3d_id in base_points3D:
        if base_p3d_id not in ext_points3D:
            missing += 1
            continue
        base_points_mat[i,:] = ext_points3D[base_p3d_id].xyz
        i += 1

    # Iterate over points of the newly added image. If any point is distant enough from the base model, return False.
    ext_p3d_distances = []
    image_registered = False
    for img in ext_images.values():
        if img.name == image_name:
            image_registered = True
            for p3d_id in img.point3D_ids:
                if p3d_id == -1:
                    continue
                p3d_xyz = ext_points3D[p3d_id].xyz
                dists = np.linalg.norm(base_points_mat - p3d_xyz, axis=1)
                min_dist = np.min(dists)
                ext_p3d_distances.append(min_dist)

    # Otherwise return True
    if image_registered:
        return max(ext_p3d_distances)
    else:
        return -1
    # return True




def register_images_multiple(original_model_path, candidates_model_path, database_path, images_path):
    # for each image:
    for img_name in os.listdir(images_path):
        # run 'register_image'
        register_image(original_model_path, candidates_model_path, database_path, images_path, img_name)
        # run 'test_image_reconstruction'
        # if 'True':
            # Accept the image. Replace the candidate model into the original model.
        shutil.rmtree(original_model_path)
        shutil.copytree(candidates_model_path, original_model_path)
        # Delete the candidate model.

    return


parser = argparse.ArgumentParser(description='')
parser.add_argument('category_index')
args = parser.parse_args()

base_model_path = f"base_models\cathedrals\{args.category_index}\sparse\\0\\"
base_db_path = f"base_models\cathedrals\{args.category_index}\database.db"

extended_model_path = f"extended_incremental\cathedrals\{args.category_index}\sparse\\0\\"
extended_db_path = f"extended_incremental\cathedrals\{args.category_index}\database.db"
extended_images_path = f"images_to_register\cathedrals\{args.category_index}\images\\"

extended_candidates_path = f"extended_incremental\cathedrals\{args.category_index}\staging\\0\\"

# Copy database.db and base model.

# if os.path.exists(extended_model_path):
#     shutil.rmtree(extended_model_path)
# if not os.path.exists(extended_model_path):
#     os.makedirs(extended_model_path)
# if not os.path.exists(extended_candidates_path):
#     os.makedirs(extended_candidates_path)
    
# shutil.copy(base_db_path, extended_db_path)
# shutil.copytree(base_model_path, extended_model_path)

# run.
# register_images_multiple(extended_model_path, extended_candidates_path, extended_db_path, extended_images_path)
images_max_dists = {}
for img_name in tqdm(os.listdir(extended_images_path)):
    images_max_dists[img_name] = test_image_reconstruction(extended_model_path, base_model_path, img_name, 0)
    


with open("test1.json", 'w') as f:
    f.write(json.dumps(images_max_dists, indent=2))






# register_image(extended_model_path, extended_candidates_path, extended_db_path, extended_images_path, "ref_img_101.jpg")