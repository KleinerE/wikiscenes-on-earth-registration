import os
import argparse
import glob

parser = argparse.ArgumentParser(description='')
parser.add_argument('--studio_renders_root')
args = parser.parse_args()

# print(args.studio_renders_root)
files = glob.glob(args.studio_renders_root + '/**/*.txt', recursive=True)

sources = set()

for filename in files:
    with open(filename, 'r') as f:
        file_sources = [s.strip() for s in f.readline().strip('\n').split(',')]
        sources.update(file_sources)

print(', '.join(sorted(sources)))

