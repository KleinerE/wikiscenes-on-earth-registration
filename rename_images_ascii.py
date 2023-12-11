import os
import shutil
import argparse
import json
from tqdm import tqdm

# parser = argparse.ArgumentParser(description='construct indexes for comparing extended model to reference models.')
# parser.add_argument('category_index')
# args = parser.parse_args()


def rename_category_images(category_images_root_path):
    # base_path = f"Data/Wikiscenes_exterior_images/cathedrals/{category_index}"
    images_input_dir = f"{category_images_root_path}/images"
    images_output_dir = f"{category_images_root_path}/images_renamed"
    if os.path.exists(images_output_dir):
        shutil.rmtree(images_output_dir)
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    renames_dict = {}
    idx = 0
    for filename in tqdm(os.listdir(images_input_dir)):
        extension = filename.split(".")[-1]
        new_filename = f"ext_img_{idx:05d}.{extension}"
        renames_dict[new_filename] = filename
        source_path = "\\\\?\\" + os.path.abspath(os.path.join(images_input_dir, filename))
        target_path = "\\\\?\\" + os.path.abspath(os.path.join(images_output_dir, new_filename))
        # shutil.copy2(os.path.join(images_input_dir, filename), os.path.join(images_output_dir, new_filename))
        shutil.copy2(source_path, target_path)
        # os.rename(os.path.join(images_dir, filename), os.path.join(images_dir, new_filename))
        idx += 1

    dict_out_path = f"{category_images_root_path}/images_new_names.json"
    with open(dict_out_path, "w") as outfile:
        json.dump(renames_dict, outfile)

    print(f"Renamed {idx+1} files.")


extended_images_directory = "..\Data\Wikiscenes_exterior_images\cathedrals"
for entry in os.scandir(extended_images_directory):
    if entry.is_dir():
        category_num = int(entry.name)
        print(f"Category: {category_num}")
        category_extended_images_dir = f"{extended_images_directory}\{category_num}"

        if not os.path.exists(category_extended_images_dir):
            print(f"Category {category_num} not found.")
            continue

        rename_category_images(category_extended_images_dir)