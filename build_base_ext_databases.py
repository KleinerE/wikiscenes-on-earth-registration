import os
import sys
import argparse
import subprocess
import datetime
import shutil

parser = argparse.ArgumentParser(description='')
parser.add_argument("--category-list-path", type=str, required=True, help="path to plain text file containing category numbers to work")
parser.add_argument("--output_dir", type=str, required=True, help="path to output dir")
args = parser.parse_args()

colmap_path = r"C:\Projects\Uni\WikiScenes-prod\COLMAP-3.9.1-windows-cuda\COLMAP.bat"
base_images_path = os.path.abspath("..\Data\StudioRenders\cathedrals")
ext_images_path = os.path.abspath("..\Data\Wikiscenes_exterior_images\cathedrals")
vocab_tree_path = os.path.abspath("..\Data\\vocab_tree_vanilla_32K.bin")

with open(args.category_list_path) as f:    
    for line in f:
        if not line.rstrip().isnumeric():
            continue

        cat_num = int(line)
        cat_dir = f"{args.output_dir}/{cat_num}"
        cat_base_dir = f"{cat_dir}/base"
        cat_ext_dir = f"{cat_dir}/ext"
        cat_base_db_path = f"{cat_base_dir}/database.db"
        cat_ext_db_path = f"{cat_ext_dir}/database.db"
        cat_base_images_path = f"{base_images_path}/{cat_num}/images"
        cat_ext_images_path = f"{ext_images_path}/{cat_num}/images_renamed"

        os.makedirs(cat_base_dir)
        os.system(f"{colmap_path} feature_extractor --database_path {cat_base_db_path} --image_path {cat_base_images_path}")
        os.system(f"{colmap_path} spatial_matcher --database_path {cat_base_db_path} --TwoViewGeometry.min_num_inliers 5")

        os.makedirs(cat_ext_dir)
        shutil.copy2(cat_base_db_path, cat_ext_db_path)

        os.system(f"{colmap_path} feature_extractor --database_path {cat_ext_db_path} --image_path {cat_ext_images_path}")
        os.system(f"{colmap_path} vocab_tree_matcher --database_path {cat_ext_db_path} --VocabTreeMatching.vocab_tree_path {vocab_tree_path} --VocabTreeMatching.num_nearest_neighbors 50 --VocabTreeMatching.num_images 1000 --TwoViewGeometry.min_num_inliers 5")