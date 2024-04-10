import os

db_path = "..\Data\\vocab_database_dsp_affine.db"

colmap_path = r"C:\Projects\Uni\WikiScenes-prod\COLMAP-3.9.1-windows-cuda\COLMAP.bat"

print("##### STUDIO RENDERS ####")
studio_renders_directory = "..\Data\StudioRenders\cathedrals"
for entry in os.scandir(studio_renders_directory):
    if entry.is_dir() and entry.name.rstrip().isnumeric():
        category_num = int(entry.name)
        print(f"Category: {category_num}")
        category_studio_renders_dir = f"{studio_renders_directory}\{category_num}\images"

        if not os.path.exists(category_studio_renders_dir):
            print(f"Category {category_num} not found.")
            continue
        
        # print(db_path)
        os.system(f"{colmap_path} feature_extractor --database_path {db_path} --image_path {category_studio_renders_dir} --SiftExtraction.domain_size_pooling 1 --SiftExtraction.estimate_affine_shape 1")

print("##### EXTERIOR PHOTOS ####")
extended_images_directory = "..\Data\Wikiscenes_exterior_images\cathedrals"
for entry in os.scandir(extended_images_directory):
    if entry.is_dir() and entry.name.rstrip().isnumeric():
        category_num = int(entry.name)
        print(f"Category: {category_num}")
        category_extended_images_dir = f"{extended_images_directory}\{category_num}\images"

        if not os.path.exists(category_extended_images_dir):
            print(f"Category {category_num} not found.")
            continue

        os.system(f"{colmap_path} feature_extractor --database_path {db_path} --image_path {category_extended_images_dir} --SiftExtraction.domain_size_pooling 1 --SiftExtraction.estimate_affine_shape 1")


