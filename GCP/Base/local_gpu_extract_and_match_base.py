import os
import subprocess
import datetime

colmap_path = r"C:\Projects\Uni\WikiScenes-prod\COLMAP-3.9.1-windows-cuda\COLMAP.bat"

def extract_and_match_features_base(images_base_path, models_base_path, category_index, additional_extractor_args, matcher_type, additional_matcher_args):

    if not os.path.isfile(colmap_path):
        print(f"COLMAP not found in path: {colmap_path}. Aborting")
        return False

    category_images_path = f"{images_base_path}\{category_index}"
    category_output_path = f"{models_base_path}\{category_index}"

    if os.path.exists(category_output_path):
        print(f"base model for category {category_index} already exists. Skipping.")
        return
    if not os.path.exists(category_output_path):
        os.makedirs(category_output_path)

    database_path = f"{category_output_path}\database.db"
    # category_model_path = f"{category_output_path}\sparse"
    
    # if not os.path.exists(category_model_path):
    #     os.makedirs(category_model_path)
    
    log_path = f"{category_output_path}\colmap_log.txt"
    arg_log_path = f"{category_output_path}\colmap_args.txt"

    # define colmap parameters
    feature_extractor_args_all = [colmap_path, "feature_extractor",
                    "--database_path", database_path,
                    "--image_path", category_images_path]

    if additional_extractor_args is not None:
        feature_extractor_args.extend(additional_extractor_args.split())

    matcher_args_all = [colmap_path, matcher_type,
                    "--database_path", database_path]

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



def run_base_multiple(category_list_path, models_base_path, images_base_path, extractor_args, matcher_type, matcher_args):
    with open(category_list_path) as f:
        for line in f:
            if line.rstrip().isnumeric():
                category_num = int(line)
                print(f"Category: {category_num}")
                extract_and_match_features_base(images_base_path, models_base_path, category_num, extractor_args, matcher_type, matcher_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--category_list_path", type=str, help="path to plain text file containing category numbers to work")
    args = parser.parse_args()

    run_base_multiple(args.category_list_path)
