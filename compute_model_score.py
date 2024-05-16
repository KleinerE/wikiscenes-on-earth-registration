import os
import argparse
import numpy as np
import json
import csv
from colmap_python_utils.read_write_model import read_model


def compute_model_DREM_score(reference_model_path_base, extended_model_path, extended_images_root):
    
    ref_models = []
    list_subfolders_with_paths = [f.path for f in os.scandir(reference_model_path_base) if f.is_dir()]
    print(f"reference model has {len(list_subfolders_with_paths)} components. Importing...")
    for i in range(len(list_subfolders_with_paths)): 
        submodel_dir = list_subfolders_with_paths[i]
        ref_cameras, ref_images, ref_points3D = read_model(submodel_dir, ext='.txt')
        print(f"#{i} -> {len(ref_images)} images  ,  {len(ref_points3D)} points")
        ref_models.append((i, ref_cameras, ref_images, ref_points3D))
    print("Done.")

    print(f"Importing extended model...")
    ext_cameras, ext_images, ext_points3D = read_model(extended_model_path, ext='.bin')
    with open(f"{extended_images_root}/images_new_names.json", 'r') as imgnamesfile:
        ext_img_orig_names = json.load(imgnamesfile)
    print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

    # Ignore all base model images
    for img in list(ext_images.keys()):
        if not ext_images[img].name.startswith('ext'):
            del ext_images[img]
    print(f"WikiScenes-only images: {len(ext_images)}.")

    print("Analyzing...")
        
    # Go over all images in extended model. for each one, find if it's in any of the reference models.
    img_ref_component_idxs = np.ones((len(ext_images))) * -1
    i = 0
    for ext_img in ext_images:
        ext_img_name = ext_img_orig_names[ext_images[ext_img].name]
        for component_idx, ref_cameras, ref_images, ref_points3D in ref_models:
            for ref_img in ref_images:
                ref_img_name = ref_images[ref_img].name.split("pictures/")[-1]
                if(ref_img_name == ext_img_name):
                    img_ref_component_idxs[i] = component_idx
                    break             
        i += 1

    print(f"Previously unregistered images: {(img_ref_component_idxs == -1).sum()}")
    for i in range(len(ref_models)):
        print(f"Previously registered in component #{i} -> {(img_ref_component_idxs == i).sum()}")

    # our new metric
    all_images_set = set(ext_img_orig_names.values())

    ext_images_set = set([ext_img_orig_names[img.name] for img in ext_images.values()])
        
    ref_images_set = set()
    for component_idx, ref_cameras, ref_images, ref_points3D in ref_models:
        ref_images_set.update([img.name.split("pictures/")[-1] for img in ref_images.values() if img.name.split("pictures/")[-1] in all_images_set])


    print(f"All images: {len(all_images_set)}")
    print(f"Ext images: {len(ext_images_set)}")
    print(f"Ref images: {len(ref_images_set)}")

    size_factor = len(ext_images_set) / len(ref_images_set)

    intersection = ext_images_set.intersection(ref_images_set)
    union = ext_images_set.union(ref_images_set)
    iou = len(intersection) / len(union)

    drem = (size_factor ** 2) * (iou ** 0.25)
    print(f"Size factor: {size_factor}")
    print(f"IoU: {iou}")
    print(f"DREM: {drem}")

    gained_images = [i for i in ext_images_set if i not in ref_images_set]
    lost_images = [i for i in ref_images_set if i not in ext_images_set]
    print(f"{len(gained_images)}, {len(lost_images)}")


    return drem, size_factor, iou, len(gained_images), len(lost_images)


parser = argparse.ArgumentParser(description='Computes extended model score based on reference model')
parser.add_argument('--category_index')
parser.add_argument('--extended_model_path')
parser.add_argument('--extended_models_root')
args = parser.parse_args()

reference_model_path_base = f"../Data/WikiScenes3D/{args.category_index}"
extended_images_root = f"../Data/Wikiscenes_exterior_images/cathedrals/{args.category_index}"

if args.extended_model_path is not None:
    compute_model_DREM_score(reference_model_path_base, args.extended_model_path, extended_images_root)

elif args.extended_models_root is not None:
    extended_category_root = f"{args.extended_models_root}/{args.category_index}"
    output_csv_path = f"{extended_category_root}/model_drem_scores.csv"
    with open(output_csv_path, 'w') as outfile:
        csv_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for entry in os.scandir(extended_category_root):
            if entry.is_dir() and entry.name.isnumeric():
                print(f"Directory: {entry.name}")
                extended_model_dir = f"{entry.path}/ext/sparse"
                drem, size_factor, iou, gained_images, lost_images = compute_model_DREM_score(reference_model_path_base, extended_model_dir, extended_images_root)
                csv_writer.writerow([int(entry.name), drem, size_factor, iou, gained_images, lost_images])

