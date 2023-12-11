import os
import subprocess
import datetime

colmap_path = r"C:\Projects\Uni\WikiScenes-prod\COLMAP-3.8-windows-cuda\COLMAP.bat"

def build_base_model(images_base_path, models_base_path, category_index):

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
    category_model_path = f"{category_output_path}\sparse"
    
    if not os.path.exists(category_model_path):
        os.makedirs(category_model_path)
    
    log_path = f"{category_output_path}\log.txt"

    # define colmap parameters
    feature_extractor_args = [colmap_path, "feature_extractor",
                    "--database_path", database_path,
                    "--image_path", category_images_path]

    matcher_args = [colmap_path, "exhaustive_matcher",
                    "--database_path", database_path]

    mapper_args = [colmap_path, "mapper",
                    "--database_path", database_path,
                    "--image_path", category_images_path,
                    "--output_path", category_model_path]

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
    print(f"[{datetime.datetime.now()}] category {category_index}: extracting features...")
    subprocess.run(feature_extractor_args, stdout=logf, stderr=subprocess.STDOUT)

    logf.close()
    
    # Run exhaustive matcher
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now()}] category {category_index}: matching features...")
    subprocess.run(matcher_args, stdout=logf, stderr=subprocess.STDOUT)
    logf.close()

    # Run mapper
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now()}] category {category_index}: mapping...")
    subprocess.run(mapper_args, stdout=logf, stderr=subprocess.STDOUT)
    
    logf.close()
    print(f"[{datetime.datetime.now()}] category {category_index}: done. Log saved to: {log_path}")

    return True


images_base_path = "..\Data\StudioRenders\cathedrals"
models_base_path = "..\Models\Base\cathedrals"

extract_stats = {}
for entry in os.scandir(images_base_path):
    if entry.is_dir():
        category_num = int(entry.name)
        print(f"Category: {category_num}")
        build_base_model(images_base_path, models_base_path, category_num)