import argparse
import numpy as np
import json
import itertools
from colmap_python_utils.read_write_model import read_model, Image, qvec2rotmat, rotmat2qvec, read_images_binary
from tqdm import tqdm
from statistics import mean, median, mode, stdev

parser = argparse.ArgumentParser(description='construct indexes for comparing extended model to reference models.')
parser.add_argument('category_index')
parser.add_argument('component_index')
args = parser.parse_args()

print(f"Importing extended model...")
extended_model_path = f"extended_models/cathedrals/{args.category_index}/sparse/0"
ext_cameras, ext_images, ext_points3D = read_model(extended_model_path, ext='.bin')
with open(f"extended_models/cathedrals/{args.category_index}/images_new_names.json", 'r') as imgnamesfile:
    ext_img_orig_names = json.load(imgnamesfile)
print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

print(f"Importing reference model...")
reference_model_path = f"WikiScenes3D/{args.category_index}/{args.component_index}"
ref_cameras, ref_images, ref_points3D = read_model(reference_model_path, ext='.txt')
print(f"Done - {len(ref_images)} images  ,  {len(ref_points3D)} points")

# ext_images = read_images_binary(f"toy_models/images_0.bin")
# ref_images = read_images_binary(f"toy_models/images_1.bin")

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

# print(ext_img_id_pairs)
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
    err_angles_w_images.append((ext_images[ext_img_id_0].name, ext_images[ext_img_id_1].name, error))
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

with open("test.txt", 'w') as f:
    f.write('\n'.join('{} -> {}, {}'.format(x[2],x[0],x[1]) for x in err_angles_w_images))

with open("test1.json", 'w') as f:
    f.write(json.dumps(image_errs_avg_sorted, indent=2))

print(mean(image_errs_avg.values()))

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

exit()






for ext_img_id_0, ext_img_id_1 in ext_img_id_pairs:
    # extract qvecs
    ext_img_0_qvec = ext_images[ext_img_id_0].qvec
    ext_img_1_qvec = ext_images[ext_img_id_1].qvec
    ref_img_id_0 = image_id_pairs[ext_img_id_0]
    ref_img_id_1 = image_id_pairs[ext_img_id_1]
    ref_img_0_qvec = ref_images[ref_img_id_0].qvec
    ref_img_1_qvec = ref_images[ref_img_id_1].qvec

    # Compute the delta rotation from image 0 to image 1, in extended model.
    delta_R_ext = quaternion_multiply(ext_img_1_qvec, qvec_inverse(ext_img_0_qvec))
    # Apply the same rotation to image 0 from reference model.
    ref_0_proj_qvec = quaternion_multiply(delta_R_ext , ref_img_0_qvec)
    # Compute the rotation error between this projection and the actual reference image 1 orientation.
    ref_rotation_err = quaternion_multiply(ref_img_1_qvec, qvec_inverse(ref_0_proj_qvec))

    w = ref_rotation_err[0]
    if w >= 1:
        w -= np.finfo(float).eps
    elif w <= -1:
        w += np.finfo(float).eps
    
    err_angle = 2 * np.arccos(w)
    # if np.isnan(err_angle):
    #     print(ref_rotation_err)
    #     print(w)
    err_angles.append(err_angle)



























# print((ext_images[1531].qvec2rotmat()))
avg_angle_errors = []

for ext_img_id_0, ext_img_id_1 in ext_img_id_pairs:
    ext_img_0_qvec = ext_images[ext_img_id_0].qvec
    ext_img_1_qvec = ext_images[ext_img_id_1].qvec
    ref_img_id_0 = image_id_pairs[ext_img_id_0]
    ref_img_id_1 = image_id_pairs[ext_img_id_1]
    ref_img_0_qvec = ref_images[ref_img_id_0].qvec
    ref_img_1_qvec = ref_images[ref_img_id_1].qvec

    # Compute the delta rotation from image 0 to image 1, in extended moel and in reference model.
    # delta_R_ext = ext_img_1_qvec.reshape(-1,1).dot(qvec_inverse(ext_img_0_qvec).reshape(-1,1).T)
    delta_R_ext = quaternion_multiply(ext_img_1_qvec, qvec_inverse(ext_img_0_qvec))
    # print("AAAAA")
    # print(ext_img_id_0)
    # print(ext_img_id_1)
    # print(ext_img_1_qvec)
    # print(qvec_inverse(ext_img_0_qvec))
    # print(delta_R_ext)
    # Not sure if needed
    # delta_q_ext = rotmat2qvec(delta_R_ext[0:3, 0:3])
    # delta_R_ref = ref_img_1_qvec.reshape(-1,1) * qvec_inverse(ref_img_0_qvec).reshape(-1,1).T
    # delta_q_ref = rotmat2qvec(delta_R_ref[0:3, 0:3])

    # Project reference image 0 with the extended model delta rotation
    # ref_0_proj_qvec = np.matmul(delta_R_ext , ref_img_0_qvec.reshape(-1,1))
    ref_0_proj_qvec = quaternion_multiply(delta_R_ext , ref_img_0_qvec)
    # print(ref_0_proj_qvec)

    # Calculate the correction term needed to reach the true image 1. (This is another rotation matrix)
    # R_ref_proj_correction = ref_img_1_qvec.reshape(-1,1) * qvec_inverse(ref_0_proj_qvec.squeeze()).reshape(-1,1).T
    model_rotation_hyp = quaternion_multiply(ref_img_1_qvec, qvec_inverse(ref_0_proj_qvec))
    # print("BBBBBBBBBBBBB")
    # print(ext_img_id_0)
    # print(ext_img_id_1)
    # print(R_ref_proj_correction)
    # print(ref_0_proj_qvec.squeeze())
    # print(qvec_conjugate(ref_0_proj_qvec.squeeze()))
    # print(qvec_inverse(ref_0_proj_qvec.squeeze()))
    # print(np.linalg.norm(ref_0_proj_qvec.squeeze()))

    # now, to measure the error, we project each reference model image along the two rotations, and calculate the rotation error.
    test_delta_angles = []
    for test_ext_img_id_0, test_ext_img_id_1 in ext_img_id_pairs:
        if test_ext_img_id_0 != ext_img_id_0 and test_ext_img_id_1 != ext_img_id_1:
            test_ref_img_id_0 = image_id_pairs[test_ext_img_id_0]
            test_ref_img_id_1 = image_id_pairs[test_ext_img_id_1]
            test_ref_img_0_qvec = ref_images[test_ref_img_id_0].qvec
            test_ref_img_1_qvec = ref_images[test_ref_img_id_1].qvec

            # Project image 0 along the proposed rotations.            
            # test_ref_img_0_proj_qvec = R_ref_proj_correction.dot(delta_R_ext.dot(test_ref_img_0_qvec))
            test_ref_img_0_proj_qvec = quaternion_multiply(model_rotation_hyp, quaternion_multiply(delta_R_ext, test_ref_img_0_qvec))
            # print(test_ref_img_0_proj_qvec)
            # Calculate the delta rotation between the result and actual image 1.
            # test_delta_R = test_ref_img_1_qvec.reshape(-1,1) * qvec_inverse(test_ref_img_0_proj_qvec).reshape(-1,1).T            
            # test_delta_qvec = rotmat2qvec(test_delta_R[0:3, 0:3])
            test_delta_qvec = quaternion_multiply(test_ref_img_1_qvec, qvec_inverse(test_ref_img_0_proj_qvec))      
            w = test_delta_qvec[0]
            if w >= 1:
                w -= np.finfo(float).eps
            elif w <= -1:
                w += np.finfo(float).eps
            # test_delta_angle = 2 * np.arccos(test_delta_qvec[0])
            test_delta_angle = 2 * np.arccos(w)
            test_delta_angles.append(test_delta_angle)

    avg_angle_errors.append(mean(test_delta_angles))
    # print(test_delta_angles)

print(min(avg_angle_errors))
print(max(avg_angle_errors))
print(mean(avg_angle_errors))

