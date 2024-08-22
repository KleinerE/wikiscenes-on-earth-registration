 
## 1. Create base images (Google Earth)

## 2. Create base models (Google Earth)

## 3. Prepare WikiScenes exterior images
1. Create an empty directory for collected images.
1. Run `py collect_exterior_images.py --input_dir <path to wikiscenes 'cathedrals' dir> --output_dir <path to your collected photos dir>`
3. Create an empty directory for renamed images.
2. Run `rename_images_ascii.py --input_dir <path to your collected photos dir> --output_dir <path to your renamed photos dir>`

## 4. Create extended models
	## 5. Search for number of inliers:
	1. Create base-ext databases.
	2. Analyze cross-dataset matches and get the inlier search bounds.
	3. Create cloud instances. (?)
	4. Iterate inliers.
		- Challenge: unintentionally creating multiple base models.
	5. Plot graphs of # of images vs. # of inliers to find
	6. iterate over candidates and create full reconstructions.
	7. Analyze candidate reconstructions qualitatively & quantitatively.
	8. Upload chosen models. (?)

	## 6. Optimal - Search across or refine other parameters if needed. 

## 5. Post-process/Analysis:
- Normalize models.
- Create scoresheets.
- Save ext-only reconstruction (optional)
