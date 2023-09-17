import numpy as np
import open3d
from colmap_python_utils.read_write_model import Image, qvec2rotmat, rotmat2qvec
from colmap_python_utils.visualize_model import draw_camera


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

def image_apply_transformation(img, T):
    T_img = get_image_world_transform(img)
    T_img_new = T @ T_img

    # COLMAP stores the image-to-world transform in the image data.
    T_img_new_inv = np.linalg.inv(T_img_new)
    R_img_new, t_img_new = split_transform(T_img_new_inv)
    return img._replace(qvec = rotmat2qvec(R_img_new), tvec = t_img_new)


def add_image(img, cameras, color=[0.8, 0.2, 0.8], scale=1, T=np.eye(4)):
    # rotation
    img_transformed = image_apply_transformation(img, T)
    R = qvec2rotmat(img_transformed.qvec)
    # translation
    t = img_transformed.tvec
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
    return cam_model    
    

def add_points(points3D, min_track_len=3, remove_statistical_outlier=True, T=np.eye(4)):
    pcd = open3d.geometry.PointCloud()

    xyz = []
    rgb = []
    for point3D in points3D.values():
        track_len = len(point3D.point2D_idxs)
        if track_len < min_track_len:
            continue
        xyzw = np.append(point3D.xyz ,1)
        xyzw = np.dot(T, xyzw)
        xyzw /= xyzw[3]
        xyz.append(xyzw[:3])
        rgb.append(point3D.rgb / 255)

    pcd.points = open3d.utility.Vector3dVector(xyz)
    pcd.colors = open3d.utility.Vector3dVector(rgb)

    # remove obvious outliers
    if remove_statistical_outlier:
        [pcd, _] = pcd.remove_statistical_outlier(nb_neighbors=20,
                                                    std_ratio=2.0)

    return pcd

def add_bbox(bbox_size=5, bbox_center=np.zeros((3,))):
    pcd = open3d.geometry.PointCloud()
    xyz = np.array([[1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0]], dtype=float)
    xyz *= bbox_size
    rgb = np.ones((4, 3))
    pcd.points = open3d.utility.Vector3dVector(xyz.tolist())
    pcd.colors = open3d.utility.Vector3dVector(rgb.tolist())
    return pcd


def get_model_center_of_mass(points3D):
    xyz_list = []
    for p3d in points3D.values():
        xyz_list.append(p3d.xyz)

    pcd = np.asarray(xyz_list)
    return np.mean(pcd, axis=0)



def render_image_pair(image0, image0_color, image1, image1_color, cameras, points3D, output_path, bbox_size=5, bbox_center=np.zeros((3,)), user_adjust_view=False, T=np.eye(4)): #, flip_image_rotations=False, R=np.eye(3)):
    __vis = open3d.visualization.Visualizer()
    __vis.create_window()

    # Set view boundary by adding a dummy point cloud 
    bbox_size = 3
    __vis.add_geometry(add_bbox(bbox_size, bbox_center))
    axis = open3d.geometry.TriangleMesh.create_coordinate_frame(size=1)
    __vis.add_geometry(axis, False)
    
    # Render cameras.
    frames = []
    frames.extend(add_image(image0, cameras, image0_color, T=T))
    frames.extend(add_image(image1, cameras, image1_color, T=T))
    for i in frames:
        __vis.add_geometry(i, False)

    # Render model
    __vis.add_geometry(add_points(points3D, T=T), False)
    # pcd = open3d.geometry.PointCloud()
    # rgb = np.zeros((1, 3))
    # xyz = get_model_center_of_mass(points3D)
    # pcd.points = open3d.utility.Vector3dVector(np.expand_dims(xyz, axis=0).tolist())
    # pcd.colors = open3d.utility.Vector3dVector(rgb.tolist())
    # __vis.add_geometry(pcd, False)

    __vis.poll_events()
    __vis.update_renderer()

    if user_adjust_view:
        __vis.run()
    __vis.capture_screen_image(output_path)
    __vis.destroy_window()



# determine by simple heuristic if image0 sees both image1 and the model's center, and same for image1.
def determine_image_pair_lineofsight(img0, img1, points3D):
    model_center = get_model_center_of_mass(points3D)
    t0 = -img0.tvec
    t1 = -img1.tvec

    t0_to_model = model_center - t0
    t1_to_model = model_center - t1
    t0_to_t1 = t1-t0

    return np.dot(t0_to_model, t0_to_t1)>=0, np.dot(t1_to_model, -t0_to_t1)>=0

# run the above tests on the extended model & reference model - if we have an agreement on one image for both models, use that image.
def determine_image_pair_best_image(ext_img0, ext_img1, ext_points3D, ref_img0, ref_img1, ref_points3D):
    l0_ext, l1_ext = determine_image_pair_lineofsight(ext_img0, ext_img1, ext_points3D)
    l0_ref, l1_ref = determine_image_pair_lineofsight(ref_img0, ref_img1, ref_points3D)
    if(l0_ext and l0_ref):
        return 0
    if(l1_ext and l1_ref):
        return 1
    return -1
