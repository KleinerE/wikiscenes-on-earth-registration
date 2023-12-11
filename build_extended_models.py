import os
import shutil
import subprocess
import datetime
import codecs

colmap_path = r"C:\Projects\Uni\WikiScenes-prod\COLMAP-3.8-windows-cuda\COLMAP.bat"

def build_extended_model(base_models_directory, extended_models_directory, extended_images_path, category_index, vocab_tree_path=''):

    if not os.path.isfile(colmap_path):
        print(f"COLMAP not found in path: {colmap_path}. Aborting")
        return False

    base_root_path = f"{base_models_directory}\{category_index}"
    if not os.path.exists(base_root_path):
        print(f"No base model found for category {category_index}")
        return False

    extended_root_path = f"{extended_models_directory}\{category_index}"
    if not os.path.exists(extended_root_path):
        os.makedirs(extended_root_path)

    base_database_path = f"{base_root_path}\database.db"
    base_sparse_model_path = f"{base_root_path}\sparse\\0"
    
    extended_database_path = f"{extended_root_path}\database.db"
    extended_sparse_model_path = f"{extended_root_path}\sparse\\0"
    if os.path.exists(extended_sparse_model_path):
        print(f"extended model already exists at path: {extended_sparse_model_path}. Skipping")
        return False
    if not os.path.exists(extended_sparse_model_path):
        os.makedirs(extended_sparse_model_path)
    
    log_path = f"{extended_root_path}\log.txt"

    # Copy base database to extended output folder, in order to extend it.
    shutil.copy(base_database_path, extended_database_path)

    # Create images_list.txt
    extended_images_list_path = f"{extended_root_path}\images_list.txt"
    with codecs.open(extended_images_list_path, "w", "utf-8") as lf:
        lf.write('\n'.join(i for i in os.listdir(extended_images_path)))

    # define colmap parameters
    feature_extractor_args = [colmap_path, "feature_extractor",
                    "--database_path", extended_database_path,
                    "--image_path", extended_images_path,
                    "--image_list_path", extended_images_list_path]

    # matcher_args = [colmap_path, "exhaustive_matcher",
    #                 "--database_path", extended_database_path,
    #                 "--SiftMatching.min_num_inliers", str(5)]

    matcher_args = [colmap_path, "vocab_tree_matcher",
                    "--database_path", extended_database_path,
                    "--SiftMatching.min_num_inliers", str(15),
                    "--VocabTreeMatching.vocab_tree_path", vocab_tree_path]

                    

    # mapper_args = [colmap_path, "mapper",
    #                 "--database_path", extended_database_path,
    #                 "--image_path", extended_images_path,
    #                 "--input_path", base_sparse_model_path,
    #                 "--output_path", extended_sparse_model_path]

    mapper_args = [colmap_path, "mapper",
                    "--database_path", extended_database_path,
                    "--image_path", extended_images_path,
                    "--input_path", base_sparse_model_path,
                    "--output_path", extended_sparse_model_path,
                    "--Mapper.ignore_watermarks", str(1),
                    "--Mapper.fix_existing_images", str(1),
                    "--Mapper.abs_pose_min_num_inliers", str(30)]

    with open(log_path, "w") as logf:
        logf.write("###############################  COLMAP ARGS  ###############################\n")
        logf.write(" ".join(arg for arg in feature_extractor_args))
        logf.write("\n")
        logf.write(" ".join(arg for arg in matcher_args))
        logf.write("\n")
        logf.write(" ".join(arg for arg in mapper_args))
        logf.write("\n")
        logf.write("#############################################################################\n")

    # Run feature extractor
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now().time()}] category {category_index}: extracting features...")
    subprocess.run(feature_extractor_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()
    
    # Run matcher
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now().time()}] category {category_index}: matching features...")
    subprocess.run(matcher_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()

    # Run mapper
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now().time()}] category {category_index}: mapping...")
    subprocess.run(mapper_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()

    print(f"[{datetime.datetime.now().time()}] category {category_index}: done. Log saved to: {log_path}")

    return True


extended_images_directory = "..\Data\Wikiscenes_exterior_images\cathedrals"
vocab_tree_path = "..\Data\\vocab_tree_flickr100K_words256K.bin"
base_models_path = "..\Models\Base\cathedrals"
extended_models_directory = "..\Models\extended_vocabtree_04\cathedrals"

extract_stats = {}
for entry in os.scandir(base_models_path):
    if entry.is_dir() and entry.name.isnumeric():
        category_num = int(entry.name)
        print(f"Category: {category_num}")
        category_extended_images_dir = f"{extended_images_directory}\{category_num}\images_renamed"
        build_extended_model(base_models_path, extended_models_directory, category_extended_images_dir, category_num, vocab_tree_path)