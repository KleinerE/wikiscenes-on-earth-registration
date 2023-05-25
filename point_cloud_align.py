import os
import argparse
import numpy as np
import numpy.linalg
from colmap_python_utils.read_write_model import read_model
from colmap_python_utils.visualize_model import Model

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



def compute_alignment(model_a_num, points3D_a, model_b_num, points3D_b, point3D_groups):
    relevant_pairs = []
    xyz_a_list = []
    xyz_b_list = []
    for group in point3D_groups:
        group_models = [int(n.split(':')[0]) for n in group]
        if model_a_num not in group_models or model_b_num not in group_models:
            continue
        group_points3D = [n.split(':')[1] for n in group]    
        p3d_a_id = int(group_points3D[group_models.index(model_a_num)])
        p3d_b_id = int(group_points3D[group_models.index(model_b_num)])
        relevant_pairs.append((p3d_a_id, p3d_b_id))
        xyz_a_list.append(points3D_a[p3d_a_id].xyz)
        xyz_b_list.append(points3D_b[p3d_b_id].xyz)

    print(f"Models have {len(relevant_pairs)} shared points.")

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



parser = argparse.ArgumentParser(description='construct indexes for comparing extended model to reference models.')
parser.add_argument('category_index')
parser.add_argument('reference_model_index')
args = parser.parse_args()

reference_path_base = f"reference_models/cathedrals/{args.category_index}"
reference_model_path_base = f"{reference_path_base}/sparse"
ref_models = []
list_subfolders_with_paths = [f.path for f in os.scandir(reference_model_path_base) if f.is_dir()]
print(f"reference model has {len(list_subfolders_with_paths)} components. Importing...")
for i in range(len(list_subfolders_with_paths)): 
    submodel_dir = list_subfolders_with_paths[i]
    ref_cameras, ref_images, ref_points3D = read_model(submodel_dir, ext='.bin')
    # print(f"#{i} -> {len(ref_images)} images  ,  {len(ref_points3D)} points")
    ref_models.append((i, ref_cameras, ref_images, ref_points3D))
print("Done.")

print(f"Importing extended model...")
extended_model_path = f"extended_models/cathedrals/{args.category_index}/sparse/0"
ext_cameras, ext_images, ext_points3D = read_model(extended_model_path, ext='.bin')
print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")


point3d_groups_path = f"{reference_path_base}/points3d_groups.json"
with open(point3d_groups_path, "r") as infile:
    point_groups = [l.split(",") for l in infile.read().splitlines()]
    print(f"Read points3D groups from {point3d_groups_path}")

point3d_groups_path_a = f"{reference_path_base}/points3d_groups_aaa.json"
with open(point3d_groups_path_a, "r") as infile:
    point_groups_without_ext = [l.split(",") for l in infile.read().splitlines()]
    print(f"Read points3D groups from {point3d_groups_path_a}")



def align_models(base_model_num, points3D_base_model, add_model_num, points3D_add_model, point3D_groups):
    c, R, t = compute_alignment(base_model_num, points3D_base_model, add_model_num, points3D_add_model, point3D_groups)
    
    for p3d in points3D_add_model:
        new_xyz = points3D_add_model[p3d].xyz.dot(c * R) + t
        points3D_add_model[p3d] = points3D_add_model[p3d]._replace(xyz=new_xyz, rgb=np.array([255, 0, 0]))
        # points3D_add_model[p3d] = points3D_add_model[p3d]._replace(rgb=np.array([255, 0, 0]))

    # for p3d in points3D_add_model:
    #     print(type(points3D_add_model[p3d]))
    #     print(points3D_add_model[p3d])
    #     break

    model = Model()
    model.create_window()

    model.points3D = points3D_base_model
    model.add_points()

    model.points3D = points3D_add_model
    model.add_points()

    model.show()

# Testing

ref_model_index = int(args.reference_model_index)
ref_points3D = ref_models[ref_model_index][3]
align_models(-1, ext_points3D, ref_model_index, ref_points3D, point_groups)
align_models(0, ref_models[0][3], ref_model_index, ref_points3D, point_groups_without_ext)






exit()

np.set_printoptions(precision=3)

a1 = np.array([
  [0, 0, -1],
  [0, 0, 0],
  [0, 0, 1],
  [0, 1, 0],
  [1, 0, 0],
])

a2 = np.array([
  [0, 0, 1],
  [0, 0, 0],
  [0, 0, -1],
  [0, 1, 0],
  [-1, 0, 0],
])
a2 *= 2 # for testing the scale calculation
a2 += 3 # for testing the translation calculation


c, R, t = umeyama(a1, a2)
print("R =\n", R)
print("c =", c)
print("t =\n", t)
print
print("Check:  a1*cR + t = a2  is", np.allclose(a1.dot(c*R) + t, a2))
err = ((a1.dot(c * R) + t - a2) ** 2).sum()
print("Residual error", err)