import argparse
from colmap_python_utils.read_write_model import read_model, write_model

parser = argparse.ArgumentParser(description='')
parser.add_argument("--input_path", type=str, required=True)
parser.add_argument("--output_path", type=str, required=True)
args = parser.parse_args()


print(f"Importing extended model...")
ext_cameras, ext_images, ext_points3D = read_model(args.input_path, ext='.bin')
print(f"Done - {len(ext_images)} images  ,  {len(ext_points3D)} points")

# Ignore all base model images
for img in list(ext_images.keys()):
    if not ext_images[img].name.startswith('ext'):
        del ext_cameras[ext_images[img].camera_id]
        del ext_images[img]
print(f"WikiScenes-only images: {len(ext_images)}.")

print("Saving cleaned model...")
write_model(ext_cameras, ext_images, ext_points3D, args.output_path ,ext='.bin')
