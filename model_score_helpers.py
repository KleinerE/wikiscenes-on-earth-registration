
import numpy as np
from colmap_python_utils.read_write_model import Image, qvec2rotmat, rotmat2qvec

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
    t = 0.5 * (np.trace(R1.T @ R2) - 1)
    t = np.min([t, 1.0 - np.finfo(float).eps])
    return np.arccos(t)