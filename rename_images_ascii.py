import os
import argparse
import json
from tqdm import tqdm
parser = argparse.ArgumentParser(description='construct indexes for comparing extended model to reference models.')
parser.add_argument('category_index')
args = parser.parse_args()

base_path = f"reference_models/cathedrals/{args.category_index}"
images_dir = f"{base_path}/images"
renames_dict = {}
idx = 0
for filename in tqdm(os.listdir(images_dir)):
    extension = filename.split(".")[-1]
    new_filename = f"ref_img_{idx}.{extension}"
    renames_dict[new_filename] = filename
    os.rename(os.path.join(images_dir, filename), os.path.join(images_dir, new_filename))

    idx += 1

dict_out_path = f"{base_path}/images_new_names.json"
with open(dict_out_path, "w") as outfile:
    json.dump(renames_dict, outfile)

print(f"Renamed {idx+1} files.")