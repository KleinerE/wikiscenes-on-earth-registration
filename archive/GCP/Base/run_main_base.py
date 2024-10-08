import os
import sys
import argparse
import subprocess
import datetime
import shutil
import re
from local_gpu_extract_and_match_base import run_base_multiple

parser = argparse.ArgumentParser(description='')
parser.add_argument("--category-list-path", type=str, required=True, help="path to plain text file containing category numbers to work")
parser.add_argument("--name", type=str, required=True, help="unique name to distinguish this run from other runs")
parser.add_argument("--extractor_args", type=str, help="args for feature extractor")
parser.add_argument("--matcher_type", type=str, nargs='?', const=1, default="spatial_matcher", help="the type of feature matcher that will be used")
parser.add_argument("--matcher_args", type=str, help="args for feature matcher")
parser.add_argument("--mapper_args", type=str, help="args for mapper")
parser.add_argument('--force', nargs='?', default=False, const=True)
args = parser.parse_args()

pattern = re.compile("^[a-z]([-a-z0-9]*[a-z0-9])?$")
if pattern.match(args.name) is None:
    print("Name cannot be used to create compute instances! Supply a name that complies with convention.")
    print("The first character must be a lowercase letter, and all the following characters must be hyphens, lowercase letters, or digits, except the last character, which cannot be a hyphen.")
    print("For details, visit: https://cloud.google.com/compute/docs/naming-resources#resource-name-format")
    exit()

images_base_path = "..\..\Data\StudioRenders\cathedrals"
models_base_path = f"..\..\Models\Base\{args.name}\cathedrals"

images_base_path = os.path.abspath(images_base_path)
models_base_path = os.path.abspath(models_base_path)

use_existing = 'n'
if(os.path.exists(models_base_path)):
    if(args.force):
        use_existing = 'y'
    else:
        use_existing = input('This run already exists on the local machine. It will not be overwritten. Do you want to use it for cloud work? (Y/n)').lower()

if use_existing == 'n':
    if os.path.exists(models_base_path):
        print(f"Overwriting {models_base_path}...")
        shutil.rmtree(models_base_path)
    print(f"Starting new local run at: {models_base_path}...")
    run_base_multiple(args.category_list_path, models_base_path, images_base_path, args.extractor_args, args.matcher_type, args.matcher_args)
    print(f"Local run completed at: {models_base_path}.")

print("Starting cloud compute instances...")

batch_path = r"C:\Projects\Uni\WikiScenes-prod\Scripts\GCP\Base\manage-instance-single-base.bat"
# processes = []

with open(args.category_list_path) as f:
    # commands = [[batch_path, str(int(line)), args.name] for line in f if line.rstrip().isnumeric()]
    # if args.mapper_args is not None:
    #     commands = [c + [f"{args.mapper_args}"] for c in commands]

    # print(commands)
    # processes = [subprocess.Popen(cmd, shell=True) for cmd in commands]
    # for p in processes:
    #     p.wait()
    commands = [' '.join([batch_path, str(int(line)), args.name]) for line in f if line.rstrip().isnumeric()]
    if args.mapper_args is not None:
        commands = [c + f" \"{args.mapper_args}\"" for c in commands]
    print(commands)
    [os.system(cmd) for cmd in commands]
    # [subprocess.run(cmd, shell=True) for cmd in commands]

print("Done launching - you can now close this window.")

