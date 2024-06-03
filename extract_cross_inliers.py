import os
import argparse
from collections import Counter

def extract_cross_inliers(matches_path, category_num):
    with open(matches_path, 'r') as f:
        image_lines = [line for line in f if '.' in line]
        print(f"Total matches: {len(image_lines)}")
        # cross_lines = [line for line in image_lines if 'images/' in line and 'ext' in line]
        cross_lines = [line for line in image_lines if f'{category_num}-' in line and 'ext' in line]
        print(f"Base-Ext cross matches: {len(cross_lines)}")
        image_names = [line.split()[0] for line in cross_lines] + [line.split()[1] for line in cross_lines]

        image_names_base = [n for n in image_names if f'{category_num}-' in n]
        image_names_ext = [n for n in image_names if f'ext' in n]
        counter_base = Counter(image_names_base)
        counter_ext = Counter(image_names_ext)
        # print(count.keys()) # equals to list(set(words))
        # print(count.values()) # counts the elements' frequency
        print(f"Base: {len(counter_base)}")
        print(f"Ext: {len(counter_ext)}")
        

        ext_matches = [line for line in image_lines if line.startswith('ext') and ' ext' in line]
        image_names = [line.split()[0] for line in ext_matches] + [line.split()[1] for line in ext_matches]
        counter_ext = Counter(image_names)
        print(f"Ext-Ext: {len(counter_ext)}")
        # print(counter_ext.keys())
        # print(counter_ext.values())

        return len(image_lines), len(cross_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--path", type=str, required=True)
    parser.add_argument("--category_num", type=int, required=True)
    args = parser.parse_args()

    extract_cross_inliers(args.path, args.category_num)
    