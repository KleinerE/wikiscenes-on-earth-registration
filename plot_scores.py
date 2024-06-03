import os
import argparse
import csv
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Computes extended model score based on reference model')
parser.add_argument('--category_index')
parser.add_argument('--extended_model_path')
parser.add_argument('--extended_models_root')
args = parser.parse_args()

if args.extended_models_root is not None:
    extended_category_root = f"{args.extended_models_root}/{args.category_index}"
    output_csv_path = f"{extended_category_root}/model_drem_scores_{args.category_index}.csv"
    fieldnames = ['inliers', 'drem', 'size_factor', 'iou', 'gained_images', 'lost_images']
    with open(output_csv_path) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames = fieldnames)
        for row in reader:
            print(f"{row['inliers']}: {row['size_factor']}")
        
        xs = [int(row['inliers']) for row in reader]
        ys = [(row['size_factor']) for row in reader]
        print(xs)
        print(ys)
        plt.plot(xs, ys)
        # plt.axis(min(xs), max(xs), min(ys), max(ys))
        plt.show()
        # csv_reader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)