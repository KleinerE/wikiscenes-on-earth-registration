import argparse
import numpy as np

from colmap_python_utils.read_write_model import read_model, write_model, qvec2rotmat, rotmat2qvec
# from model_visualization import image_apply_transformation

def create_transform(R, t):
    T = np.column_stack((R, t))
    T = np.vstack((T, (0, 0, 0, 1)))
    return T

def split_transform(T):
    R = T[:3, :3]
    t = T[:3, 3].squeeze()
    return R, t

def get_image_inverse_transform(img):
    # COLMAP stores the image-to-world transform in the image data.
    R = qvec2rotmat(img.qvec)
    t = img.tvec
    return create_transform(R, t)

def get_image_world_transform(img):
    # COLMAP stores the image-to-world transform in the image data.
    # To get the world-to-image transform, we take the inverse.
    T_inv = get_image_inverse_transform(img)
    return np.linalg.inv(T_inv)

def image_apply_transformation(img, offset, scale):
    T_img = get_image_world_transform(img)

    T_translate = np.eye(4)
    T_translate[0,3] = offset[0]
    T_translate[1,3] = offset[1]
    T_translate[2,3] = offset[2]
    T_img_new = T_translate @ T_img
    
    T_img_new[0,3] *= scale
    T_img_new[1,3] *= scale
    T_img_new[2,3] *= scale

    # COLMAP stores the image-to-world transform in the image data.
    T_img_new_inv = np.linalg.inv(T_img_new)
    R_img_new, t_img_new = split_transform(T_img_new_inv)
    return img._replace(qvec = rotmat2qvec(R_img_new), tvec = t_img_new)




parser = argparse.ArgumentParser(description='Computes extended model score based on reference model')
parser.add_argument('--input_path')
parser.add_argument('--output_path')
args = parser.parse_args()

print(f"Importing extended model...")
ext_cameras, ext_images, ext_points3D = read_model(args.input_path, ext='.bin')
print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

xyz_list = []
for p3d in ext_points3D.values():
    xyz_list.append(p3d.xyz)

pcd = np.asarray(xyz_list)

scale = 1.0 / np.std(pcd, axis=0)[1]
offset = -1.0 * np.mean(pcd, axis=0)
print(f"offset: {offset}. scale: {scale}")


for p3d in ext_points3D:
    xyz_new = (ext_points3D[p3d].xyz + offset) * scale
    ext_points3D[p3d] = ext_points3D[p3d]._replace(xyz = xyz_new)

for img in ext_images:
    ext_images[img] = image_apply_transformation(ext_images[img], offset, scale)


print(f"Writing transformed model...")
write_model(ext_cameras, ext_images, ext_points3D, args.output_path, ext='.bin')
print(f"Done.")