import os
import argparse
import subprocess
import datetime
from base_models_local_gpu_work import run_base_multiple

parser = argparse.ArgumentParser(description='')
parser.add_argument("--category_list_path", type=str, help="path to plain text file containing category numbers to work")
args = parser.parse_args()

# run_base_multiple(args.category_list_path)

print("Starting compute instances...")

batch_path = r"C:\Projects\Uni\WikiScenes-prod\Scripts\GCP\manage-instance-single.bat"
processes = []
with open(args.category_list_path) as f:
    commands = [[batch_path, str(int(line))] for line in f if line.rstrip().isnumeric()]
    print(commands)
    processes = [subprocess.Popen(cmd, shell=True) for cmd in commands]
    for p in processes:
        p.wait()

print("Done")

