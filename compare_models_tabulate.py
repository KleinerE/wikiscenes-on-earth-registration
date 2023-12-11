import os
from tqdm import tqdm 
from colmap_python_utils.read_write_model import read_model
from tabulate import tabulate

models_root = "..\Models"
base_root = f"{models_root}\Base\cathedrals"
extended_roots = ["extended_exhaustive", "extended_vocabtree_00", "extended_vocabtree_01", "extended_vocabtree_02", "extended_vocabtree_03", "extended_vocabtree_04"]

categories = [entry.name for entry in os.scandir(base_root) if entry.is_dir() and entry.name.isnumeric()]

headers = ["Category", "Base Model"]
headers.extend(extended_roots)

table = []
for category in categories:
    print(f"Processing category {category}")
    base_path = f"{base_root}\{category}\sparse\\0"
    base_cameras, base_images, base_points3D = read_model(base_path, ext='.bin')
    cat_row = [category, str(len(base_images))]
    for ext_root in tqdm(extended_roots):
        ext_path = f"{models_root}\{ext_root}\cathedrals\{category}\sparse\\0"
        if(os.path.exists(ext_path) and len(os.listdir(ext_path)) > 0):
            ext_cameras, ext_images, ext_points3D = read_model(ext_path, ext='.bin')
            cat_row.append(str(len(ext_images)))
        else:
            cat_row.append("--")
    table.append(cat_row)

print(tabulate(table, headers=headers))