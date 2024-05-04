import os
import subprocess
import datetime
import argparse
import shutil

colmap_path = r"C:\Projects\Uni\WikiScenes-prod\COLMAP-3.9.1-windows-cuda\COLMAP.bat"

def build_model(output_path, category_index, num_inliers, base_images_path, ext_images_path, vocab_tree_path):

    # Base
    base_dir = f"{output_path}\\base"
    os.makedirs(base_dir)
    base_sparse_dir = f"{base_dir}\\sparse"
    os.makedirs(base_sparse_dir)

    base_database_path = f"{base_dir}\database.db"
    
    log_path = f"{base_dir}\colmap_log.txt"
    arg_log_path = f"{base_dir}\colmap_args.txt"

    ## define colmap parameters
    base_extractor_args = [colmap_path, "feature_extractor",
                    "--database_path", base_database_path,
                    "--image_path", base_images_path]

    base_matcher_args = [colmap_path, "spatial_matcher",
                    "--database_path", base_database_path,
                    "--TwoViewGeometry.min_num_inliers", str(num_inliers)]

    base_mapper_args = [colmap_path, "mapper",
                    "--database_path", base_database_path,
                    "--image_path", base_images_path,
                    "--output_path", base_sparse_dir,
                    "--Mapper.min_num_matches", str(num_inliers),
                    "--Mapper.ignore_watermarks", str(1)]

    with open(arg_log_path, "w") as logf:
        logf.write(" ".join(arg for arg in base_extractor_args))
        logf.write("\n")
        logf.write(" ".join(arg for arg in base_matcher_args))
        logf.write("\n")
        logf.write(" ".join(arg for arg in base_mapper_args))
        logf.write("\n")

    ## Run feature extractor
    logf = open(log_path, "w")
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, base: extracting features...")
    subprocess.run(base_extractor_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()
    
    ## Run exhaustive matcher
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, base: matching features...")
    subprocess.run(base_matcher_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()

    ## Run mapper
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, base: mapping...")
    subprocess.run(base_mapper_args, stdout=logf, stderr=subprocess.STDOUT)
    
    logf.close()
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, base: done. Log saved to: {log_path}")

    #######

    # Ext

    ext_dir = f"{output_path}\\ext"
    os.makedirs(ext_dir)
    ext_sparse_dir = f"{ext_dir}\\sparse"
    os.makedirs(ext_sparse_dir)
    
    ## copy base database
    ext_database_path = f"{ext_dir}\database.db"
    shutil.copy2(base_database_path, ext_database_path)

    log_path = f"{ext_dir}\colmap_log.txt"
    arg_log_path = f"{ext_dir}\colmap_args.txt"

    ## define colmap parameters
    ext_extractor_args = [colmap_path, "feature_extractor",
                    "--database_path", ext_database_path,
                    "--image_path", ext_images_path]

    ext_matcher_args = [colmap_path, "vocab_tree_matcher",
                    "--database_path", ext_database_path,
                    "--VocabTreeMatching.vocab_tree_path", vocab_tree_path,
                    "--VocabTreeMatching.num_nearest_neighbors", str(50),
                    "--VocabTreeMatching.num_images", str(1000),
                    "--TwoViewGeometry.min_num_inliers", str(num_inliers)]

    ext_mapper_args = [colmap_path, "mapper",
                    "--database_path", ext_database_path,
                    "--image_path", ext_images_path,
                    "--input_path", f"{base_sparse_dir}\\0"
                    "--output_path", ext_sparse_dir,
                    "--Mapper.min_num_matches", str(num_inliers),
                    "--Mapper.fix_existing_images", str(1),
                    "--Mapper.tri_max_transitivity", str(3),
                    "--Mapper.tri_ignore_two_view_tracks", str(0),
                    "--Mapper.abs_pose_max_error", str(36),
                    "--Mapper.ba_global_max_refinement_change", str(0.0015)]

    with open(arg_log_path, "w") as logf:
        logf.write(" ".join(arg for arg in ext_extractor_args))
        logf.write("\n")
        logf.write(" ".join(arg for arg in ext_matcher_args))
        logf.write("\n")
        logf.write(" ".join(arg for arg in ext_mapper_args))
        logf.write("\n")

    ## Run feature extractor
    logf = open(log_path, "w")
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, extended: extracting features...")
    subprocess.run(ext_extractor_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()
    
    ## Run exhaustive matcher
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, extended: matching features...")
    subprocess.run(ext_matcher_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()

    ## Run mapper
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, extended: mapping...")
    subprocess.run(ext_mapper_args, stdout=logf, stderr=subprocess.STDOUT)
    
    logf.close()
    print(f"[{datetime.datetime.now()}] category {category_index}, inliers={num_inliers}, extended: done. Log saved to: {log_path}")


###############################################################################################    

parser = argparse.ArgumentParser(description='')
parser.add_argument("--model_list_path", type=str, required=True)
parser.add_argument("--output_path", type=str, required=True)
args = parser.parse_args()



base_images_root = os.path.abspath("..\Data\StudioRenders\cathedrals")
ext_images_root = os.path.abspath("..\Data\Wikiscenes_exterior_images\cathedrals")
vocab_tree_path = os.path.abspath("..\Data\\vocab_tree_flickr100K_words32K.bin")

if not os.path.isfile(colmap_path):
    print(f"COLMAP not found in path: {colmap_path}. Aborting")
    exit()

with open(args.model_list_path) as f:
    for line in f:
        category_num = int(line.split(':')[0].strip())
        inliers_list = [int(n) for n in line.split(':')[1].strip().split(',')]
        print("######")
        print(f"[{datetime.datetime.now()}] category {category_num}, inliers list: {inliers_list}")
        base_images_path = f"{base_images_root}\{category_num}\images"
        ext_images_path = f"{ext_images_root}\{category_num}\images_renamed"

        for inliers_num in inliers_list:
            print(f"[{datetime.datetime.now()}] category {category_num}, current num inliers: {inliers_num}")
            output_path = f"{args.output_path}/{category_num}/{inliers_num}"
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            
            build_model(output_path, category_num, inliers_num, base_images_path, ext_images_path, vocab_tree_path)