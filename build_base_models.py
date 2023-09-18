import os
import subprocess
import datetime

colmap_path = r"D:\Projects\WikiScenes\COLMAP-3.8-windows-no-cuda\COLMAP.bat"

def build_base_model(images_base_path, models_base_path, category_index):

    if not os.path.isfile(colmap_path):
        print(f"COLMAP not found in path: {colmap_path}. Aborting")
        return False

    category_images_path = f"{images_base_path}\{category_index}"
    category_output_path = f"{models_base_path}\{category_index}"

    if not os.path.exists(category_output_path):
        os.makedirs(category_output_path)

    database_path = f"{base_output_path}\database.db"
    category_model_path = f"{base_output_path}\sparse"
    
    if not os.path.exists(category_model_path):
        os.makedirs(category_model_path)
    
    log_path = f"{base_output_path}\log.txt"

    # Run feature extractor
    logf = open(log_path, "w")
    print(f"[{datetime.datetime.now().time()}] category {category_index}: extracting features...")
    subprocess.run([colmap_path, "feature_extractor",
                    "--database_path", database_path,
                    "--image_path", images_path,
                    "--SiftExtraction.use_gpu", "false"], stdout=logf, stderr=subprocess.STDOUT)

    logf.close()
    
    # Run exhaustive matcher
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now().time()}] category {category_index}: matching features...")
    subprocess.run([colmap_path, "exhaustive_matcher",
                    "--database_path", database_path,
                    "--SiftMatching.use_gpu", "false"], stdout=logf, stderr=subprocess.STDOUT)
    logf.close()

    # Run mapper
    logf = open(log_path, "a")
    print(f"[{datetime.datetime.now().time()}] category {category_index}: mapping...")
    subprocess.run([colmap_path, "mapper",
                    "--database_path", database_path,
                    "--image_path", category_images_path,
                    "--output_path", category_model_path], stdout=logf, stderr=subprocess.STDOUT)
    
    logf.close()
    print(f"[{datetime.datetime.now().time()}] category {category_index}: done. Log saved to: {log_path}")

    return True


images_base_path = ".\Data\StudioRenders\cathedrals"
models_base_path = ".\Models\Base\cathedrals"

extract_stats = {}
for entry in os.scandir(images_base_path):
    if entry.is_dir():
        category_num = int(entry.name)
        print(f"Category: {category_num}")
        build_base_model(images_base_path, models_base_path, category_num)