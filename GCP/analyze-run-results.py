import os
import argparse
import subprocess
import shutil

parser = argparse.ArgumentParser(description='')
parser.add_argument("--category-list-path", type=str, required=True, help="path to plain text file containing category numbers to work")
parser.add_argument("--run-type", choices=['base', 'ext', 'extended'], required=True, help="wether this is a base model or an extended model.")
parser.add_argument("--run-name", type=str, required=True, help="the name of this run")
parser.add_argument("--row-name", choices=['images', 'registered', 'points', 'track-length', 'observations', 'reproj'], help="name of row")
args = parser.parse_args()

row_dict={  'images': 1,
            'registered': 2,
            'points': 3,
            'track-length': 5,
            'observations': 6,
            'reproj': 7}

run_type = 'extended' if args.run_type == 'ext' else args.run_type

# s = subprocess.run([shutil.which('gsutil'), "cat", "gs://cwge-test-bucket-0/base/pipe-test-01/5/analysis.txt"], capture_output=True)
# print(s.stdout.decode('utf-8').split('\n')[row_dict[args.row_name]].split("] ")[1])
# exit()
with open(args.category_list_path) as f:
    categories = [int(line) for line in f if line.rstrip().isnumeric()]
    commands = [[shutil.which('gsutil'), "cat", f"gs://cwge-test-bucket-0/{run_type}/{args.run_name}/{i}/analysis.txt"] for i in categories]
    whole_analysis_files = [subprocess.run(cmd, capture_output=True).stdout.decode('utf-8') for cmd in commands]
    relevant_rows = [a.split('\n')[row_dict[args.row_name]] if len(a)>0 else '' for a in whole_analysis_files]
    split_lines=[r.split("] ")[-1] for r in relevant_rows]
    [print(f"{int(category)}: {s}") for category, s in zip(categories, split_lines)]
