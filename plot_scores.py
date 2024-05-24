import os
import argparse
import csv
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Computes extended model score based on reference model')
parser.add_argument('--csv_path')
args = parser.parse_args()

fieldnames = ['inliers', 'drem', 'size_factor', 'iou', 'gained_images', 'lost_images']

styles = ['o-', '^-', 'v-', 'X-', 'D-', '*-']
i=0
categories = []
for csv_file_name in os.listdir(args.csv_path):
    with open(f"{args.csv_path}/{csv_file_name}") as csvfile:
        reader = list(csv.DictReader(csvfile, fieldnames = fieldnames))
        xs = [int(row['inliers']) for row in reader]
        ys = [float(row['drem']) for row in reader]
        print(csv_file_name.split('.')[0].split('_')[-1])
        plt.plot(xs, ys, styles[i])
        categories.append(csv_file_name.split('.')[0].split('_')[-1])
    i += 1

plt.legend(categories, title="category")
plt.grid()
plt.title("Data Increase Ratio (>1 => more data)")
plt.xlabel("# of Inliers")
plt.ylabel("Extended Model Images / Reference Model Images")
plt.show()



# fieldnames = ['inliers', 'mean_orientation_err', 'num_common_images']

# styles = ['o-', '^-', 'v-', 'X-', 'D-', '*-']
# i=0
# categories = []
# for csv_file_name in os.listdir(args.csv_path):
#     with open(f"{args.csv_path}/{csv_file_name}") as csvfile:
#         reader = list(csv.DictReader(csvfile, fieldnames = fieldnames))
#         xs = [int(row['inliers']) for row in reader if int(row['num_common_images']) > 5]
#         ys = [float(row['mean_orientation_err']) for row in reader if int(row['num_common_images']) > 5]
#         print(csv_file_name.split('.')[0].split('_')[-2])
#         plt.plot(xs, ys, styles[i])
#         categories.append(csv_file_name.split('.')[0].split('_')[-2])
#     i += 1


# plt.legend(categories, title="category")
# plt.grid()
# plt.title("Mean Image Orientation Error")
# plt.xlabel("# of Inliers")
# plt.ylabel("Geodesic Error (rad)")
# plt.show()