import numpy as np
import colmap_python_utils.read_write_model as rwm
# from colmap_python_utils.visualize_model import Model

def euler2quat(euler): # roll (x), pitch (Y), yaw (z)
    roll = euler[0]
    pitch = euler[1]
    yaw = euler[2]

    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)

    q = np.zeros(4)
    q[0] = cr * cp * cy + sr * sp * sy
    q[1] = sr * cp * cy - cr * sp * sy
    q[2] = cr * sp * cy + sr * cp * sy
    q[3] = cr * cp * sy - sr * sp * cy

    return q


images = {}
N = 10
id_start = 10
noise_strength = 0.1
include_noise = True
for i in range(0, N):
    noise = include_noise * np.random.normal(0, noise_strength) # * np.ones(3)
    
    angle = np.pi * i / N # * np.ones(3)
    # qvec = euler2quat(np.array([0, angle + noise, 0]))
    qvec = euler2quat(np.array([angle + noise, 0, 0]))
    
    # tvec = np.array([0, i + noise, 0])
    tvec = np.array([i + noise, 0, 0])
    # tvec = np.zeros(3)

    # print(f"i = {i}:")
    # print(angle)
    # print(noise)
    print(qvec)

    image_id = id_start + i
    camera_id=0
    image_name=f"toy_image_{image_id-id_start}"
    xys = []
    point3D_ids = []
    images[image_id] = rwm.Image(
                    id=image_id, qvec=qvec, tvec=tvec,
                    camera_id=camera_id, name=image_name,
                    xys=xys, point3D_ids=point3D_ids)

rwm.write_images_binary(images, f"toy_models/images_1.bin")