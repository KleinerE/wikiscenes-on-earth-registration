import os
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument("--path", type=str, required=True)
args = parser.parse_args()

# inliers_path = r"..\..\..\analysis_space\ext-lower-inliers-00\9\inliers.txt"

with open(args.path, 'r') as f:
    image_lines = [line for line in f if '.' in line]
    print(f"Total matches: {len(image_lines)}")
    # cross_lines = [line for line in image_lines if 'images/' in line and 'ext' in line]
    cross_lines = [line for line in image_lines if '0-' in line and 'ext' in line]
    print(f"Base-Ext cross matches: {len(cross_lines)}")
    # [print(line) for line in cross_lines]