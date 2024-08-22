import os
import shutil
import argparse
import json

def rename_category_images(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    renames_dict = {}
    idx = 0
    for filename in os.listdir(input_dir):
        extension = filename.split(".")[-1]
        new_filename = f"ext_img_{idx:05d}.{extension}"
        renames_dict[new_filename] = filename
        source_path = "\\\\?\\" + os.path.abspath(os.path.join(input_dir, filename))
        target_path = "\\\\?\\" + os.path.abspath(os.path.join(output_dir, new_filename))
        shutil.copy2(source_path, target_path)
        idx += 1

    print(f"Renamed {idx+1} files.")
    return renames_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs sequentially on all images in a directory and renames them to sequentially-named standardized names, in a pattern of 'ext_img_#####'. This is done mainly to ensure that all names are ASCII-compatible so that COLMAP doesn't skip any images and also for ease of use later on.")
    parser.add_argument("--input_dir", type=str, required=True, help="path to exterior images base dir, or to a single exterior images category dir if --single_category is specified.")
    parser.add_argument("--output_dir", type=str, required=True, help="path to output dir.")
    parser.add_argument("--single_category", action='store_true', help="is this flag is specified, the input dir is treated as a single category.")
    args = parser.parse_args()

    if args.single_category:
        renames_dict = rename_category_images(args.input_dir, args.output_dir)
        dict_out_path = f"{args.output_dir}\{category_num}\images_new_names.json"
        with open(dict_out_path, "w") as outfile:
            json.dump(renames_dict, outfile)

    else:
        for entry in os.scandir(args.input_dir):
            if entry.is_dir():
                category_num = int(entry.name)
                print(f"Category: {category_num}")
                renames_dict = rename_category_images(f"{args.input_dir}\{category_num}", f"{args.output_dir}\{category_num}")

                dict_out_path = f"{args.output_dir}\{category_num}\images_new_names.json"
                with open(dict_out_path, "w") as outfile:
                    json.dump(renames_dict, outfile)