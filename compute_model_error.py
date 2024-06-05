import os
import argparse
import numpy as np
import json
import csv
import itertools
import shutil
from statistics import mean, median, mode, stdev
from colmap_python_utils.read_write_model import read_model, Image, qvec2rotmat, rotmat2qvec, read_images_binary
from model_score_helpers import geodesic_error


def compute_model_orientation_error(extended_model_path, extended_images_root, reference_model_path):
    # Load models.
    print(f"Importing extended model...")
    if not os.path.exists(extended_model_path):
        return -1, 0, []
    if len(os.listdir(extended_model_path)) == 0:
        return -1, 0, []
    ext_cameras, ext_images, ext_points3D = read_model(extended_model_path, ext='.bin')
    with open(f"{extended_images_root}/images_new_names.json", 'r') as imgnamesfile:
        ext_img_orig_names = json.load(imgnamesfile)
    print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

    print(f"Importing reference model...")
    ref_cameras, ref_images, ref_points3D = read_model(reference_model_path, ext='.txt')
    print(f"Done - {len(ref_images)} images  ,  {len(ref_points3D)} points")

    # Build a mapping between extended model image ID to reference model image ID.
    ext2ref_id_map = {}
    for ext_img_id in ext_images:
        ext_img_new_name = ext_images[ext_img_id].name
        if ext_img_new_name in ext_img_orig_names:
            ext_img_orig_name = ext_img_orig_names[ext_img_new_name]
            for ref_img_id in ref_images:
                ref_img_name = ref_images[ref_img_id].name.split('/')[-1] # WikiScenes3D image names have a 'full' relative path instead of just the image name.
                if(ref_img_name == ext_img_orig_name):
                    ext2ref_id_map[ext_img_id] = ref_img_id

    print(f"\nModels have {len(ext2ref_id_map)} common images.")

    if(len(ext2ref_id_map) == 0):
        return -1, 0, []

    print("\n Computing image orientation error")

    # Go over pairs of images and calculate delta rotations

    ## get all possible pairs of images
    ext_img_id_pairs = list(itertools.combinations(ext2ref_id_map.keys(), 2))
    # ref_img_id_pairs = list(itertools.combinations(ext2ref_id_map.values(), 2))

    err_angles = [] # list of all orientation errors (one for each image pair)
    err_angles_w_images = [] # list of tuples - (id0, id1, error)
    image_errs = {} # mapping of <image id> -> <list of all relevant errors>. will be used to determine most and least accurate images.

    for ext_img_id_0, ext_img_id_1 in ext_img_id_pairs:
        # extract qvecs
        ext_img_0_qvec = ext_images[ext_img_id_0].qvec
        ext_img_1_qvec = ext_images[ext_img_id_1].qvec
        ref_img_id_0 = ext2ref_id_map[ext_img_id_0]
        ref_img_id_1 = ext2ref_id_map[ext_img_id_1]
        ref_img_0_qvec = ref_images[ref_img_id_0].qvec
        ref_img_1_qvec = ref_images[ref_img_id_1].qvec

        # Compute the rotation from image 0 to image 1, in extended model.
        delta_R_ext = qvec2rotmat(ext_img_1_qvec) @ np.linalg.inv(qvec2rotmat(ext_img_0_qvec))
        # Compute the angle between image 0 to image 1, in reference model. (not sure if needed)
        delta_R_ref = qvec2rotmat(ref_img_1_qvec) @ np.linalg.inv(qvec2rotmat(ref_img_0_qvec))

        # for image 0, compute the rotation from extension space to reference space.
        R_ext_to_ref_0 = qvec2rotmat(ref_img_0_qvec) @ np.linalg.inv(qvec2rotmat(ext_img_0_qvec))
        # Apply this rotation to the extension image 1 to obtain the hypothesized reference image 1 orientation.
        ref_1_eval = delta_R_ext @ R_ext_to_ref_0 @ qvec2rotmat(ext_img_0_qvec)
        # The error is the geodesic distance between this hypothesis and 'ground truth' (the actual reference image 1 orientation)
        error = geodesic_error(qvec2rotmat(ref_img_1_qvec), ref_1_eval)

        err_angles.append(error)
        # err_angles_w_images.append((ext_images[ext_img_id_0].name, ext_images[ext_img_id_1].name, error))
        err_angles_w_images.append((ext_img_id_0, ext_img_id_1, error))
        if ext_images[ext_img_id_0].name not in image_errs:
            image_errs[ext_images[ext_img_id_0].name] = []
        image_errs[ext_images[ext_img_id_0].name].append(error)
        if ext_images[ext_img_id_1].name not in image_errs:
            image_errs[ext_images[ext_img_id_1].name] = []
        image_errs[ext_images[ext_img_id_1].name].append(error)

    image_errs_avg = {} # mapping of <image id> -> <median error value>
    for k, v in image_errs.items():
        image_errs_avg[k] = median(v)

    ## sort images by median error -> most accurate images are at the top. 
    image_errs_avg_sorted = dict(sorted(image_errs_avg.items(), key=lambda item: item[1]))

    ## sort tuples by error -> most accurate image pair is at the top and least accurate pair is at the bottom.
    image_pairs_sorted = sorted(err_angles_w_images, key=lambda item: item[2])

    ## finally - the orientation score is simply the mean image orientation error (across all common images).
    if len(image_errs_avg) == 0:
        return -1, 0, []

    print(f"orientation score: {mean(image_errs_avg.values())}")

    return mean(image_errs_avg.values()), len(ext2ref_id_map), image_pairs_sorted


parser = argparse.ArgumentParser(description='')
parser.add_argument('--category_index')
parser.add_argument('--w3d_component_index')
parser.add_argument('--extended_model_path')
parser.add_argument('--extended_models_root')
parser.add_argument('--user_view_adjust', nargs='?', default=False, const=True)
args = parser.parse_args()

extended_images_root = f"../Data/Wikiscenes_exterior_images/cathedrals/{args.category_index}"
reference_model_path = f"../Data/WikiScenes3D/{args.category_index}/{args.w3d_component_index}"

if args.extended_models_root is not None:
    extended_category_root = f"{args.extended_models_root}/{args.category_index}"
    output_csv_path = f"{extended_category_root}/model_orientation_errors_{args.category_index}_{args.w3d_component_index}.csv"
    with open(output_csv_path, 'w') as outfile:
        csv_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for entry in os.scandir(extended_category_root):
            if entry.is_dir() and entry.name.isnumeric():
                print(f"Directory: {entry.name}")
                extended_model_dir = f"{entry.path}/ext/sparse"
                mean_orientation_err, num_common_images, image_pairs_sorted = compute_model_orientation_error(extended_model_dir, extended_images_root, reference_model_path)
                if mean_orientation_err >= 0:
                    csv_writer.writerow([int(entry.name), mean_orientation_err, num_common_images])

# Comment this out to proceed to visualizations.
exit()

# elif args.extended_model_path is not None:
#     compute_model_DREM_score(reference_model_path_base, args.extended_model_path, extended_images_root)

# Visualize.
from output_model_score_html import ScoresheetData, create_scoresheet
from model_visualization import create_transform, determine_image_pair_best_image, get_image_inverse_transform, render_image_pair

extended_model_output_root = f"{args.extended_model_path}/score"
pair_visualizations_path = os.path.abspath(f"{extended_model_output_root}/image_pair_vis/")
extended_images_path_absolute = os.path.abspath(f"{extended_images_root}/images_renamed")

if os.path.exists(extended_model_output_root):
    shutil.rmtree(extended_model_output_root)
if not os.path.exists(extended_model_output_root):
    os.makedirs(extended_model_output_root)
    os.makedirs(pair_visualizations_path)


orientation_errors_out_path = f"{extended_model_output_root}/orientation_errors.txt"
with open(orientation_errors_out_path, 'w') as f:
    f.write(f"{mean(image_errs_avg.values())}\n")
    f.write('\n'.join('{},{},{}'.format(x[2],x[0],x[1]) for x in image_pairs_sorted))

print(f"wrote orientation errors to: {orientation_errors_out_path}")

## visualization consts
uva=args.user_view_adjust

bbox_center_ref = np.array([2,2,0])
image0_color = [0.2, 0.2, 0.9]
image1_color = [0.9, 0.2, 0.2]

# "view" transform relative to chosen image - rotate along x axis by 210 degrees and move forwards & upwards.
R_view = qvec2rotmat([-0.258819, 0.9659258, 0, 0])
t_view = ([0, -1.5, 4])
T_view = create_transform(R_view, t_view)

s = ScoresheetData()
s.orientation_score = mean(image_errs_avg.values())
s.image_color_0 = image0_color
s.image_color_1 = image1_color


def create_image_pair_visualizations(img0_id, img1_id, error, img0_color, img1_color, name, T_view, user_view_adjust=False):
    ext_img0 = ext_images[img0_id]
    ext_img1 = ext_images[img1_id]
    ref_img0 = ref_images[ext2ref_id_map[img0_id]]
    ref_img1 = ref_images[ext2ref_id_map[img1_id]]
    chosen_idx = determine_image_pair_best_image(ext_img0, ext_img1, ext_points3D, ref_img0, ref_img1, ref_points3D)

    setattr(s, f"ornt_img_{name}_0", os.path.join(extended_images_path_absolute, ext_img0.name))
    setattr(s, f"ornt_img_{name}_1", os.path.join(extended_images_path_absolute, ext_img1.name))
    setattr(s, f"ornt_{name}_error",error)

    # extended model space
    T_chosen_img_inv = get_image_inverse_transform(ext_img1) if chosen_idx == 1 else get_image_inverse_transform(ext_img0)
    T_scene = T_view @ T_chosen_img_inv

    vis_path = f"{pair_visualizations_path}/{name}_extended.png"
    render_image_pair(ext_img0, img0_color, ext_img1, img1_color, ext_cameras, ext_points3D, vis_path, user_adjust_view=uva, T=T_scene)
    setattr(s, f"ornt_vis_{name}_ext", vis_path)

    ## reference model space
    T_chosen_img_inv = get_image_inverse_transform(ref_img1) if chosen_idx == 1 else get_image_inverse_transform(ref_img0)
    T_scene = T_view @ T_chosen_img_inv

    vis_path = f"{pair_visualizations_path}/{name}_reference.png"
    render_image_pair(ref_img0, img0_color, ref_img1, img1_color, ref_cameras, ref_points3D, vis_path, user_adjust_view=uva, T=T_scene)
    setattr(s, f"ornt_vis_{name}_ref", vis_path)


## most accurate pair (lowest error)
img0_id = image_pairs_sorted[0][0]
img1_id = image_pairs_sorted[0][1]
error = image_pairs_sorted[0][2]
create_image_pair_visualizations(img0_id, img1_id, error, image0_color, image1_color, "low_0", T_view, user_view_adjust=uva)

## 2nd accurate pair
img0_id = image_pairs_sorted[1][0]
img1_id = image_pairs_sorted[1][1]
error = image_pairs_sorted[1][2]
create_image_pair_visualizations(img0_id, img1_id, error, image0_color, image1_color, "low_1", T_view, user_view_adjust=uva)

## 3rd accurate pair
img0_id = image_pairs_sorted[2][0]
img1_id = image_pairs_sorted[2][1]
error = image_pairs_sorted[2][2]
create_image_pair_visualizations(img0_id, img1_id, error, image0_color, image1_color, "low_2", T_view, user_view_adjust=uva)

## least accurate pair (highest error)
img0_id = image_pairs_sorted[-1][0]
img1_id = image_pairs_sorted[-1][1]
error = image_pairs_sorted[-1][2]
create_image_pair_visualizations(img0_id, img1_id, error, image0_color, image1_color, "high_0", T_view, user_view_adjust=uva)

## 2nd least accurate pair
img0_id = image_pairs_sorted[-2][0]
img1_id = image_pairs_sorted[-2][1]
error = image_pairs_sorted[-2][2]
create_image_pair_visualizations(img0_id, img1_id, error, image0_color, image1_color, "high_1", T_view, user_view_adjust=uva)

## 3rd least accurate pair
img0_id = image_pairs_sorted[-3][0]
img1_id = image_pairs_sorted[-3][1]
error = image_pairs_sorted[-3][2]
create_image_pair_visualizations(img0_id, img1_id, error, image0_color, image1_color, "high_2", T_view, user_view_adjust=uva)


create_scoresheet(s, extended_model_output_root)

exit()


# Relevant links:
#   - http://stackoverflow.com/a/32244818/263061 (solution with scale)
#   - "Least-Squares Rigid Motion Using SVD" (no scale but easy proofs and explains how weights could be added)


# Rigidly (+scale) aligns two point clouds with know point-to-point correspondences
# with least-squares error.
# Returns (scale factor c, rotation matrix R, translation vector t) such that
#   Q = P*cR + t
# if they align perfectly, or such that
#   SUM over point i ( | P_i*cR + t - Q_i |^2 )
# is minimised if they don't align perfectly.
def umeyama(P, Q):
    assert P.shape == Q.shape
    n, dim = P.shape

    centeredP = P - P.mean(axis=0)
    centeredQ = Q - Q.mean(axis=0)

    C = np.dot(np.transpose(centeredP), centeredQ) / n

    V, S, W = np.linalg.svd(C)
    d = (np.linalg.det(V) * np.linalg.det(W)) < 0.0

    if d:
        S[-1] = -S[-1]
        V[:, -1] = -V[:, -1]

    R = np.dot(V, W)

    varP = np.var(P, axis=0).sum()
    c = 1/varP * np.sum(S) # scale factor

    t = Q.mean(axis=0) - P.mean(axis=0).dot(c*R)

    return c, R, t


def compute_alignment(ext_images, ref_images, ext2ref_id_map):
    xyz_a_list = []
    xyz_b_list = []
    for ext_img_id, ref_img_id in ext2ref_id_map.items():
        xyz_a_list.append(ext_images[ext_img_id].tvec)
        xyz_b_list.append(ref_images[ref_img_id].tvec)

    if(len(ext2ref_id_map) < 3):
        return -1, 0, 0

    pc_a = np.asarray(xyz_a_list)
    pc_b = np.asarray(xyz_b_list)

    c, R, t = umeyama(pc_b, pc_a)
    # print("R =\n", R)
    # print("c =", c)
    # print("t =\n", t)
    # print("Check:  a1*cR + t = a2  is", np.allclose(pc_a.dot(c*R) + t, pc_b))
    # err = ((pc_a.dot(c * R) + t - pc_b) ** 2).sum()
    err = ((pc_b.dot(c * R) + t - pc_a) ** 2).mean()    
    print("Residual error", err)
    return c, R, t

print("\n Computing image position error")
compute_alignment(ext_images, ref_images, ext2ref_id_map)



import seaborn as sns
import matplotlib.pyplot as plt
# sns.set_style('whitegrid')
# sns.kdeplot(np.array(err_angles), bw_adjust=0.05)
sns.displot(np.array(err_angles))
plt.show()
