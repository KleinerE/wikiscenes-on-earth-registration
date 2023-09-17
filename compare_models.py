import os
import shutil
import argparse
import json
import numpy as np
from tqdm import tqdm 
from colmap_python_utils.read_write_model import read_model, qvec2rotmat
from model_visualization import create_transform, determine_image_pair_best_image, get_image_inverse_transform, render_image_pair
from output_model_score_html import CompareScoresheetData, create_compare_sheet


parser = argparse.ArgumentParser(description='')
parser.add_argument('model_0_root')
parser.add_argument('model_1_root')
args = parser.parse_args()

# Load models.
print(f"Importing model 0...")
model_0_path = f"{args.model_0_root}/sparse/0"
model_0_absolute = os.path.abspath(args.model_0_root)
model_0_images = f"{args.model_0_root}/images/"
model_0_images_absolute = os.path.abspath(model_0_images)
model_0_output_root = f"{args.model_0_root}/score"

cameras_0, images_0, points3D_0 = read_model(model_0_path, ext='.bin')

with open(f"{args.model_0_root}/images_new_names.json", 'r') as imgnamesfile:
    img_0_orig_names = json.load(imgnamesfile)

with open(f"{model_0_output_root}/orientation_errors.txt", 'r') as f:
    lines = f.readlines()
    model_0_orientation_score_overall = float(lines[0])
    model_0_orientation_errors_str = [tuple(l.strip('\n').split(',')) for l in lines[1:]] 
    model_0_orientation_errors = [(float(t[0]), int(t[1]), int(t[2])) for t in model_0_orientation_errors_str] 

print(f"Done - {len(images_0)} images  ,  {len(points3D_0)} points, overall score {model_0_orientation_score_overall}, {len(model_0_orientation_errors)} image pairs")


print(f"Importing model 1...")
model_1_path = f"{args.model_1_root}/sparse/0"
model_1_absolute = os.path.abspath(args.model_1_root)
model_1_images = f"{args.model_1_root}/images/"
model_1_images_absolute = os.path.abspath(model_1_images)
model_1_output_root = f"{args.model_1_root}/score"

cameras_1, images_1, points3D_1 = read_model(model_1_path, ext='.bin')

with open(f"{args.model_1_root}/images_new_names.json", 'r') as imgnamesfile:
    img_1_orig_names = json.load(imgnamesfile)

with open(f"{model_1_output_root}/orientation_errors.txt", 'r') as f:
    lines = f.readlines()
    model_1_orientation_score_overall = float(lines[0])
    model_1_orientation_errors_str = [tuple(l.strip('\n').split(',')) for l in lines[1:]] 
    model_1_orientation_errors = [(float(t[0]), int(t[1]), int(t[2])) for t in model_1_orientation_errors_str] 

print(f"Done - {len(images_1)} images  ,  {len(points3D_1)} points, overall score {model_1_orientation_score_overall}, {len(model_1_orientation_errors)} image pairs")

comparison_output_path = f"{args.model_0_root}/compare"
visualizations_path = f"{comparison_output_path}/visualizations"
visualizations_path_absolute = os.path.abspath(visualizations_path)
if os.path.exists(comparison_output_path):
    shutil.rmtree(comparison_output_path)
if not os.path.exists(comparison_output_path):
    os.makedirs(comparison_output_path)
    os.makedirs(visualizations_path)
    
with open(f"{comparison_output_path}/args.txt", "w") as f:
    f.write(f"model_0_root: {args.model_0_root}\n")
    f.write(f"model_1_root: {args.model_1_root}\n")
    
print(f"Finding matching pairs...")
tup_pairs = []
image_pairs_0 = []
image_pairs_1 = []

for err_0, id0_0, id1_0 in model_0_orientation_errors:
    for err_1, id0_1, id1_1 in model_1_orientation_errors:
        if images_1[id0_1].name == images_0[id0_0].name and images_1[id1_1].name == images_0[id1_0].name:
            image_pairs_0.append((err_0, id0_0, id1_0))
            image_pairs_1.append((err_1, id0_1, id1_1))
            tup_pairs.append(((err_0, id0_0, id1_0),(err_1, id0_1, id1_1)))
            break

print(f"Done - {len(tup_pairs)} matches found.")

# image_pairs_0_sorted = sorted(image_pairs_0, key=lambda item: item[0])
# image_pairs_1_sorted = sorted(image_pairs_1, key=lambda item: item[0])
pair0_lowest = tup_pairs[0]
pair0_highest = tup_pairs[-1]

tup_pairs_sorted_err_1 = sorted(tup_pairs, key=lambda item: item[1][0])
pair1_lowest = tup_pairs_sorted_err_1[0]
pair1_highest = tup_pairs_sorted_err_1[-1]


# Visualize.
## visualization consts
print(f"Creating visualizations and scoresheet...")

uva=False

bbox_center_ref = np.array([2,2,0])
image0_color = [0.2, 0.9, 0.6]
image1_color = [0.6, 0.6, 0.2]

# "view" transform relative to chosen image - rotate along x axis by 210 degrees and move forwards & upwards.
R_view = qvec2rotmat([-0.258819, 0.9659258, 0, 0])
t_view = ([0, -1.5, 4])
T_view = create_transform(R_view, t_view)

s = CompareScoresheetData()
s.orientation_score_0 = model_0_orientation_score_overall
s.orientation_score_1 = model_1_orientation_score_overall
s.image_color_0 = image0_color
s.image_color_1 = image1_color


def create_image_pair_visualizations(tup_pair, img0_color, img1_color, name, T_view, user_view_adjust=False):
    img0_0 = images_0[tup_pair[0][1]]
    img1_0 = images_0[tup_pair[0][2]]
    img0_1 = images_1[tup_pair[1][1]]
    img1_1 = images_1[tup_pair[1][2]]
    chosen_idx = determine_image_pair_best_image(img0_0, img1_0, points3D_0, img0_1, img1_1, points3D_1)
    
    setattr(s, f"ornt_img_{name}_0", os.path.join(model_0_images_absolute, img0_0.name))
    setattr(s, f"ornt_img_{name}_1", os.path.join(model_0_images_absolute, img1_0.name))
    setattr(s, f"ornt_{name}_error0",tup_pair[0][0])
    setattr(s, f"ornt_{name}_error1",tup_pair[1][0])

    # extended model space
    T_chosen_img_inv = get_image_inverse_transform(img1_0) if chosen_idx == 1 else get_image_inverse_transform(img0_0)
    T_scene = T_view @ T_chosen_img_inv

    vis_path = f"{visualizations_path_absolute}/{name}_0.png"
    render_image_pair(img0_0, img0_color, img1_0, img1_color, cameras_0, points3D_0, vis_path, user_adjust_view=uva, T=T_scene)
    setattr(s, f"ornt_vis_{name}_0", vis_path)

    ## reference model space
    T_chosen_img_inv = get_image_inverse_transform(img1_1) if chosen_idx == 1 else get_image_inverse_transform(img0_1)
    T_scene = T_view @ T_chosen_img_inv

    vis_path = f"{visualizations_path_absolute}/{name}_1.png"
    render_image_pair(img0_1, img0_color, img1_1, img1_color, cameras_1, points3D_1, vis_path, user_adjust_view=uva, T=T_scene)
    setattr(s, f"ornt_vis_{name}_1", vis_path)


## most accurate pair (lowest error)
create_image_pair_visualizations(pair0_lowest, image0_color, image1_color, "low_0", T_view, user_view_adjust=uva)
create_image_pair_visualizations(pair1_lowest, image0_color, image1_color, "low_1", T_view, user_view_adjust=uva)
create_image_pair_visualizations(pair0_highest, image0_color, image1_color, "high_0", T_view, user_view_adjust=uva)
create_image_pair_visualizations(pair1_highest, image0_color, image1_color, "high_1", T_view, user_view_adjust=uva)

create_compare_sheet(s, comparison_output_path)