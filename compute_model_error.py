import os
import argparse
import numpy as np
import json
import itertools
from tqdm import tqdm
from statistics import mean, median, mode, stdev
from colmap_python_utils.read_write_model import read_model, Image, qvec2rotmat, rotmat2qvec, read_images_binary
from colmap_python_utils.visualize_model import draw_camera
import open3d
from output_model_score_html import ScoresheetData, create_scoresheet

parser = argparse.ArgumentParser(description='construct indexes for comparing extended model to reference models.')
parser.add_argument('category_index')
parser.add_argument('component_index')
args = parser.parse_args()

print(f"Importing extended model...")
extended_model_path = f"extended_models/cathedrals/{args.category_index}_new/sparse/0"
extended_images_path = f"extended_models/cathedrals/{args.category_index}_new/images/"
extended_images_path_absolute = os.path.abspath(extended_images_path)
ext_cameras, ext_images, ext_points3D = read_model(extended_model_path, ext='.bin')
with open(f"extended_models/cathedrals/{args.category_index}_new/images_new_names.json", 'r') as imgnamesfile:
    ext_img_orig_names = json.load(imgnamesfile)
print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

print(f"Importing reference model...")
reference_model_path = f"WikiScenes3D/{args.category_index}/{args.component_index}"
ref_cameras, ref_images, ref_points3D = read_model(reference_model_path, ext='.txt')
print(f"Done - {len(ref_images)} images  ,  {len(ref_points3D)} points")

# Find image pairs
image_id_pairs = {}
for ext_img_id in ext_images:
    ext_img_new_name = ext_images[ext_img_id].name
    if ext_img_new_name in ext_img_orig_names:
        ext_img_orig_name = ext_img_orig_names[ext_img_new_name]
    # ext_img_orig_name = ext_img_new_name
        for ref_img_id in ref_images:
            ref_img_name = ref_images[ref_img_id].name.split('/')[-1] # WikiScenes3D image names have a 'full' relative path instead of just the image name.
            if(ref_img_name == ext_img_orig_name):
                image_id_pairs[ext_img_id] = ref_img_id

print(f"\nModels have {len(image_id_pairs)} common images.")

if(len(image_id_pairs) == 0):
    exit()

print("\n Computing image orientation error")

### Go over pairs (of pairs) and calculate delta rotations

# get all possible pairs of pairs
ext_img_id_pairs = list(itertools.combinations(image_id_pairs.keys(), 2))
ref_img_id_pairs = list(itertools.combinations(image_id_pairs.values(), 2))

def qvec_conjugate(qvec):
    return np.array([qvec[0], -1 * qvec[1], -1 * qvec[2], -1 * qvec[3]])

def qvec_norm(qvec):
    return np.dot(qvec, qvec_conjugate(qvec))

def qvec_inverse(qvec):
    return qvec_conjugate(qvec) * (1/np.linalg.norm(qvec))

def quaternion_multiply(quaternion1, quaternion0):
    w0, x0, y0, z0 = quaternion0
    w1, x1, y1, z1 = quaternion1
    return np.array([-x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0,
                     x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
                     -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
                     x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0], dtype=np.float64)

def quaternion_angle(qvec):
    w = qvec[0]
    if w >= 1:
        w -= np.finfo(float).eps
    elif w <= -1:
        w += np.finfo(float).eps
    
    w = np.clip(w, -1, 1)
        
    # if np.isnan(np.arccos(w)):
    #     print(qvec)
    return 2 * np.arccos(w)

def clamp_angle(a):
    if a > np.pi:
        a -= 2 * np.pi
    elif a < - np.pi:
        a += 2 * np.pi
    return a

def geodesic_error(R1, R2):
    return np.arccos(0.5 * (np.trace(R1.T @ R2) - 1))

err_angles = []
err_angles_w_images = []
image_errs = {}

for ext_img_id_0, ext_img_id_1 in ext_img_id_pairs:
    # extract qvecs
    ext_img_0_qvec = ext_images[ext_img_id_0].qvec
    ext_img_1_qvec = ext_images[ext_img_id_1].qvec
    ref_img_id_0 = image_id_pairs[ext_img_id_0]
    ref_img_id_1 = image_id_pairs[ext_img_id_1]
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

    # error = geodesic_error(delta_R_ext, delta_R_ref)
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
    # err_angles.append(angle_ext - angle_ref)


# print(f"number of pairs: {len(err_angles)}")
# print(f"min angle error: {min(err_angles)}")
# print(f"max angle error: {max(err_angles)}")
# print(f"avg angle error: {mean(err_angles)}")
# print(f"median angle error: {median(err_angles)}")
# print(f"mode angle error: {mode(err_angles)}")
image_errs_avg = {}
for k, v in image_errs.items():
    image_errs_avg[k] = median(v)

image_errs_avg_sorted = dict(sorted(image_errs_avg.items(), key=lambda item: item[1]))

# with open("test.txt", 'w') as f:
#     f.write('\n'.join('{} -> {}, {}'.format(x[2],x[0],x[1]) for x in err_angles_w_images))

# with open("test1.json", 'w') as f:
#     f.write(json.dumps(image_errs_avg_sorted, indent=2))

print(f"orientation score: {mean(image_errs_avg.values())}")

image_pairs_sorted = sorted(err_angles_w_images, key=lambda item: item[2])
# with open("test_sorted.txt", 'w') as f:
#     f.write('\n'.join('{} -> {}, {}'.format(x[2],x[0],x[1]) for x in image_pairs_sorted))


frames = []
def add_image(img, cameras, color=[0.8, 0.2, 0.8], scale=1):
    # rotation
    R = qvec2rotmat(img.qvec)
    # translation
    t = img.tvec
    # invert
    t = -R.T @ t
    R = R.T

    # intrinsics
    cam = cameras[img.camera_id]

    if cam.model in ("SIMPLE_PINHOLE", "SIMPLE_RADIAL", "RADIAL"):
        fx = fy = cam.params[0]
        cx = cam.params[1]
        cy = cam.params[2]
    elif cam.model in ("PINHOLE", "OPENCV", "OPENCV_FISHEYE", "FULL_OPENCV"):
        fx = cam.params[0]
        fy = cam.params[1]
        cx = cam.params[2]
        cy = cam.params[3]
    else:
        raise Exception("Camera model not supported")

    # intrinsics
    K = np.identity(3)
    K[0, 0] = fx
    K[1, 1] = fy
    K[0, 2] = cx
    K[1, 2] = cy

    # create axis, plane and pyramed geometries that will be drawn
    cam_model = draw_camera(K, R, t, cam.width, cam.height, scale, color)    
    frames.extend(cam_model)

def add_points(points3D, min_track_len=3, remove_statistical_outlier=True):
    pcd = open3d.geometry.PointCloud()

    xyz = []
    rgb = []
    for point3D in points3D.values():
        track_len = len(point3D.point2D_idxs)
        if track_len < min_track_len:
            continue
        xyz.append(point3D.xyz)
        rgb.append(point3D.rgb / 255)

    pcd.points = open3d.utility.Vector3dVector(xyz)
    pcd.colors = open3d.utility.Vector3dVector(rgb)

    # remove obvious outliers
    if remove_statistical_outlier:
        [pcd, _] = pcd.remove_statistical_outlier(nb_neighbors=20,
                                                    std_ratio=2.0)

    return pcd
    # __vis.add_geometry(pcd, False)
    # __vis.poll_events()
    # __vis.update_renderer()


frames.append(add_points(ext_points3D))
add_image(ext_images[image_pairs_sorted[0][0]], ext_cameras, [1, 0.9, 0])
add_image(ext_images[image_pairs_sorted[0][1]], ext_cameras, [0.6, 0.6, 0.2])

open3d.visualization.draw_geometries(frames,
                                    zoom=0.05,
                                    front=[0, -1, 0], # unit vector -> the direction of camera 'front'.
                                    lookat=[0, 0, 0], # vector -> the point in world to look at. affects the position of the camera.
                                    up=[0, 0, 1]) # unit vector -> the direciton of camera 'up'.


exit()
# Create data for scoresheet
s = ScoresheetData()
s = s._replace(orientation_score = mean(image_errs_avg.values()))

s = s._replace(ornt_img_low_0_0 = os.path.join(extended_images_path_absolute, image_pairs_sorted[0][0]))
s = s._replace(ornt_img_low_0_1 = os.path.join(extended_images_path_absolute, image_pairs_sorted[0][1]))
s = s._replace(ornt_img_low_1_0 = os.path.join(extended_images_path_absolute, image_pairs_sorted[1][0]))
s = s._replace(ornt_img_low_1_1 = os.path.join(extended_images_path_absolute, image_pairs_sorted[1][1]))
s = s._replace(ornt_img_low_2_0 = os.path.join(extended_images_path_absolute, image_pairs_sorted[2][0]))
s = s._replace(ornt_img_low_2_1 = os.path.join(extended_images_path_absolute, image_pairs_sorted[2][1]))

s = s._replace(ornt_img_high_0_0 = os.path.join(extended_images_path_absolute, image_pairs_sorted[-1][0]))
s = s._replace(ornt_img_high_0_1 = os.path.join(extended_images_path_absolute, image_pairs_sorted[-1][1]))
s = s._replace(ornt_img_high_1_0 = os.path.join(extended_images_path_absolute, image_pairs_sorted[-2][0]))
s = s._replace(ornt_img_high_1_1 = os.path.join(extended_images_path_absolute, image_pairs_sorted[-2][1]))
s = s._replace(ornt_img_high_2_0 = os.path.join(extended_images_path_absolute, image_pairs_sorted[-3][0]))
s = s._replace(ornt_img_high_2_1 = os.path.join(extended_images_path_absolute, image_pairs_sorted[-3][1]))

create_scoresheet(s, extended_model_path)

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


def compute_alignment(ext_images, ref_images, image_id_pairs):
    xyz_a_list = []
    xyz_b_list = []
    for ext_img_id, ref_img_id in image_id_pairs.items():
        xyz_a_list.append(ext_images[ext_img_id].tvec)
        xyz_b_list.append(ref_images[ref_img_id].tvec)

    if(len(image_id_pairs) < 3):
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
compute_alignment(ext_images, ref_images, image_id_pairs)



import seaborn as sns
import matplotlib.pyplot as plt
# sns.set_style('whitegrid')
# sns.kdeplot(np.array(err_angles), bw_adjust=0.05)
sns.displot(np.array(err_angles))
plt.show()



# for i in frames:
    # __vis.add_geometry(i, False)


# open3d.visualization.draw_geometries(frames,
#                                     zoom=0.03,
#                                     front=[10, -10, 10],
#                                     # lookat=[-0.41566, 0.0339, 1.95306],
#                                     lookat=[0, 0, 0],
#                                     up=[0, -1, 0])


# __vis.poll_events()
# __vis.update_renderer()

# __vis.run()
# __vis.destroy_window()


# # # Create a renderer with the desired image size
# img_width = 640
# img_height = 480
# render = open3d.visualization.rendering.OffscreenRenderer(img_width, img_height)
# exit()

# __vis = open3d.visualization.Visualizer()
# __vis.create_window()

# print(__vis.get_view_control().convert_to_pinhole_camera_parameters().extrinsic)
# ctr = __vis.get_view_control()
# #This line will obtain the default camera parameters .
# camera_params = ctr.convert_to_pinhole_camera_parameters() 
# extrinsic_mat = np.eye(4)
# extrinsic_mat[0][0] = -1
# extrinsic_mat[2][2] = -1
# extrinsic_mat[0][3] = 1000
# camera_params.extrinsic = extrinsic_mat
# # leaving camera intrinsics untouched
# ctr.convert_from_pinhole_camera_parameters(camera_params)

# # __vis.set_view_status(json.loads('view_status.json'))
# print(__vis.get_view_control().convert_to_pinhole_camera_parameters().extrinsic)

