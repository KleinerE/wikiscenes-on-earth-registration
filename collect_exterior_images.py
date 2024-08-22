import os
import json
import argparse
import re
import shutil

def extract_for_category(input_dir, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the base json file and find the subcategoryies that contain 'exterior'.
    with open(f"{input_dir}\category.json", encoding="utf-8") as jsonfile:
        parsed_json = json.load(jsonfile)

    subcategories = parsed_json['pairs']
    subcategories_exterior = [key for key in subcategories.keys() if re.search("exterior", key, re.IGNORECASE)]
    if(len(subcategories_exterior) == 0):
        print("There is no 'exterior' subcategory in the selected category!")

    def extract_recursive(directory_path, target_directory_path, collected_so_far, skipped_so_far):
        # print("searching in {0}...".format(directory_path))
        # if 'pictures' directory exists, copy all its contents to the target directory.
        picutres_dir = f"{directory_path}\pictures\\"
        if(os.path.exists(picutres_dir)):        
            for fname in os.listdir(picutres_dir):
                source_file_path = os.path.join(picutres_dir,fname)
                if (os.path.exists(source_file_path)):
                    target_path = "\\\\?\\" + os.path.abspath(os.path.join(target_directory_path,fname))
                    # print(target_path)
                    shutil.copy2(os.path.join(picutres_dir,fname), target_path)
                    collected_so_far+=1
                    print('Collected %d images.\r'%collected_so_far, end="")
                else:
                    skipped_so_far.append(source_file_path)
                    # print("file skipped: {0}".format(source_file_path))            

        # if 'categories.json' file exists, and it contains sub-categories, find any matching subcategories and go into them recursively.
        categories_file = f"{directory_path}\category.json"
        if(os.path.exists(categories_file)):
            with open(categories_file, 'r', encoding="utf-8") as jsonfile:
                data = jsonfile.read()
                cat_parsed_json = json.loads(data)
            
            cat_subcategories = cat_parsed_json['pairs']
            cat_subcategories_exterior = [key for key in cat_subcategories.keys() if not re.search('(interior|from|art)', key, re.IGNORECASE)]
            for subcat in cat_subcategories_exterior:
                # print("going to search in {0}\{1}...".format(directory_path,cat_subcategories[subcat]))
                collected_so_far, skipped_so_far = extract_recursive(f"{directory_path}\{cat_subcategories[subcat]}", target_directory_path, collected_so_far, skipped_so_far)

        return collected_so_far, skipped_so_far



    # For each of that main subcategory, run recursively and extract photos where the matching categories don't contain the words 'interior', 'from', 'art'
    collected = 0
    skipped = []
    for subcat in subcategories_exterior:
        collected, skipped = extract_recursive(f"{input_dir}\{subcategories[subcat]}", output_dir, collected, skipped)

    print(f"\nCollected {collected} images.")
    if(len(skipped) > 0):
        print(f"skipped files ({len(skipped)}):")
        for f in skipped:
            print(f)
    
    if collected == 0:
        cat_dir = os.path.dirname(output_dir)
        os.rmdir(output_dir)
        # os.rmdir(cat_dir)

    return collected, skipped


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Runs recursively on an entire WikiScenes dataset, or a single wikiscenes category, and copies all photos of the exterior to a separate folder.')
    parser.add_argument("--input_dir", type=str, required=True, help="path to WikiScenes base dir, or to a single WikiScenes category dir if --single_category is specified.")
    parser.add_argument("--output_dir", type=str, required=True, help="path to output dir.")
    parser.add_argument("--single_category", action='store_true', help="is this flag is specified, the input dir is treated as a single category.")
    args = parser.parse_args()

    extract_stats = {}
    if args.single_category:
        collected, skipped = extract_for_category(args.input_dir, args.output_dir)
        print(f"Collected: {collected}, skipped: {len(skipped)}")

    else:
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
 
        for entry in os.scandir(args.input_dir):
            if entry.is_dir():
                category_num = int(entry.name)
                print(f"Category: {category_num}")
                collected, skipped = extract_for_category(f"{args.input_dir}\{category_num}", f"{args.output_dir}\{category_num}")
                extract_stats[category_num] = (collected, len(skipped))    

        stats_out_path = f"{args.output_dir}\collect_stats.json"
        with open(stats_out_path, "w") as outfile:
            json.dump(extract_stats, outfile, indent=4)
            print(f"Stats saved to: {stats_out_path}")