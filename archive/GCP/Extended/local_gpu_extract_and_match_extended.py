import os
import subprocess
import datetime
import shutil
import codecs

colmap_path = r"C:\Projects\Uni\WikiScenes-prod\COLMAP-3.9.1-windows-cuda\COLMAP.bat"

def extract_and_match_features_extended(extended_models_directory, extended_images_path, category_index, additional_extractor_args, matcher_type, additional_matcher_args, vocab_tree_path=''):

    if not os.path.isfile(colmap_path):
        print(f"COLMAP not found in path: {colmap_path}. Aborting")
        return False

    extended_root_path = f"{extended_models_directory}\{category_index}"
    
    extended_database_path = f"{extended_root_path}\database.db"
    extended_sparse_model_path = f"{extended_root_path}\sparse\\0"
    if os.path.exists(extended_sparse_model_path):
        print(f"extended model already exists at path: {extended_sparse_model_path}. Skipping")
        return False
    if not os.path.exists(extended_sparse_model_path):
        os.makedirs(extended_sparse_model_path)
    
    log_path = f"{extended_root_path}\colmap_log.txt"
    arg_log_path = f"{extended_root_path}\colmap_args.txt"

    # Create images_list.txt
    extended_images_list_path = f"{extended_root_path}\images_list.txt"
    with codecs.open(extended_images_list_path, "w", "utf-8") as lf:
        lf.write('\n'.join(i for i in os.listdir(extended_images_path)))
    
    # define colmap parameters
    feature_extractor_args_all = [colmap_path, "feature_extractor",
                    "--database_path", extended_database_path,
                    "--image_path", extended_images_path,
                    "--image_list_path", extended_images_list_path]
	
    if additional_extractor_args is not None:
        feature_extractor_args_all.extend(additional_extractor_args.split())

    matcher_args_all = [colmap_path, matcher_type,
                    "--database_path", extended_database_path]
                    # "--TwoViewGeometry.min_num_inliers", str(5),
                    # "--VocabTreeMatching.vocab_tree_path", vocab_tree_path]
                    
    if matcher_type == 'vocab_tree_matcher':
        matcher_args_all.extend(["--VocabTreeMatching.vocab_tree_path", vocab_tree_path])
		
    if additional_matcher_args is not None:
        matcher_args_all.extend(additional_matcher_args.split())
        
    # mapper_args = [colmap_path, "mapper",
    #                 "--database_path", database_path,
    #                 "--image_path", category_images_path,
    #                 "--output_path", category_model_path]

    with open(arg_log_path, "w") as logf:
        logf.write(" ".join(arg for arg in feature_extractor_args_all))
        logf.write("\n")
        logf.write(" ".join(arg for arg in matcher_args_all))
        logf.write("\n")
        # logf.write(" ".join(arg for arg in mapper_args))
        # logf.write("\n")

    # Run feature extractor
    logf = open(log_path, "w")
    print(f"[{datetime.datetime.now()}] category {category_index}: extracting features...")
    subprocess.run(feature_extractor_args_all, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()
    
    # Run exhaustive matcher
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now()}] category {category_index}: matching features...")
    subprocess.run(matcher_args_all, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()

    # # Run mapper
    # logf = open(log_path, "a")
    # print(f"[{datetime.datetime.now()}] category {category_index}: mapping...")
    # subprocess.run(mapper_args, stdout=logf, stderr=subprocess.STDOUT)
    
    logf.close()
    print(f"[{datetime.datetime.now()}] category {category_index}: done. Log saved to: {log_path}")

    return True

def fetch_base_db(base_run_name, category_index, extended_models_directory):
    target_dir = f"{extended_models_directory}\{category_index}"
    print(f"Fetching base DB to: {target_dir}...")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    gsutil_args = [shutil.which('gsutil'), 
                    "cp", 
                    f"gs://cwge-test-bucket-0/base/{base_run_name}/{category_index}/database.db", 
                    target_dir]
    subprocess.run(gsutil_args)
    print(f"Done.")

def run_ext_multiple(category_list_path, extended_models_directory, extended_images_root, base_run_name, extractor_args, matcher_type, matcher_args, vocab_tree_path=''):
    with open(category_list_path) as f:
        for line in f:
            if line.rstrip().isnumeric():
                category_num = int(line)
                print(f"Category: {category_num}") 
                if not os.path.exists(f"{extended_models_directory}\{category_num}"):
                    fetch_base_db(base_run_name, category_num, extended_models_directory)
                    extended_images_directory = f"{extended_images_root}\{category_num}\images_renamed"
                    extract_and_match_features_extended(extended_models_directory, extended_images_directory, category_num, extractor_args, matcher_type, matcher_args, vocab_tree_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--category_list_path", type=str, help="path to plain text file containing category numbers to work")
    args = parser.parse_args()

    run_base_multiple(args.category_list_path)
