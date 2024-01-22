import os
import sys
import argparse
import subprocess
import datetime
import shutil
from extended_models_local_gpu_work import run_ext_multiple

parser = argparse.ArgumentParser(description='')
parser.add_argument("--category-list-path", type=str, required=True, help="path to plain text file containing category numbers to work")
parser.add_argument("--extended_run_name", type=str, required=True, help="unique name to distinguish this run from other runs")
parser.add_argument("--base_run_name", type=str, required=True, help="the name of the base model to extend")
parser.add_argument('--force', nargs='?', default=False, const=True)
args = parser.parse_args()

extended_images_root = os.path.abspath("..\..\Data\Wikiscenes_exterior_images\cathedrals")
base_models_directory = os.path.abspath(f"..\..\Models\Base\{args.base_run_name}\cathedrals")
ext_models_directory = os.path.abspath(f"..\..\Models\Extended\{args.extended_run_name}\cathedrals")
vocab_tree_path = os.path.abspath("..\..\Data\\vocab_tree_flickr100K_words32K.bin")

if not os.path.exists(base_models_directory):
    print(f"the specified base models directory does not exist: {base_models_directory}. Aborting.")
    exit()

use_existing = 'n'
if(os.path.exists(ext_models_directory)):
    if(args.force):
        use_existing = 'y'
    else:
        use_existing = input('This extended run already exists on the local machine. It will not be overwritten. Do you want to use it for cloud work? (Y/n)').lower()

if use_existing == 'n':
    if os.path.exists(ext_models_directory):
        print(f"Overwriting {ext_models_directory}...")
        shutil.rmtree(ext_models_directory)
    print(f"Starting new local run at: {ext_models_directory}...")
    run_ext_multiple(args.category_list_path, ext_models_directory, extended_images_root, args.base_run_name, vocab_tree_path)
    print(f"Local run completed at: {ext_models_directory}.")

print("Starting cloud compute instances...")

batch_path = r"C:\Projects\Uni\WikiScenes-prod\Scripts\GCP\extended-manage-instance-single.bat"
processes = []

with open(args.category_list_path) as f:
    commands = [[batch_path, str(int(line)), args.extended_run_name, args.base_run_name] for line in f if line.rstrip().isnumeric()]
    print(commands)
    processes = [subprocess.Popen(cmd, shell=True) for cmd in commands]
    for p in processes:
        p.wait()

print("Done launching - you can now close this window.")

