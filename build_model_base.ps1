param([Int32] $category_index,
        [switch] $Reference = $false)  

if($Reference)
{
    $base_images_path = ".\reference_models\cathedrals\$category_index\images\"
    $base_output_path = ".\reference_models\cathedrals\$category_index"
}
else {
    $base_images_path = ".\StudioRenders\cathedrals\$category_index\images\"
    $base_output_path = ".\base_models\cathedrals\$category_index"
}

md -Force $base_output_path

$database_path = "$base_output_path\database.db"
$sparse_output_path = "$base_output_path\sparse"
md -Force $sparse_output_path

$log_path_extraction = "$base_output_path\log_reconstruction.txt"
$log_path = "$base_output_path\log_reconstruction.txt"
$log_error_path = "$base_output_path\log_reconstruction_error.txt"

$colmap="C:\Projects\Uni\COLMAP-3.7-windows-cuda\COLMAP.bat"
if(Test-Path $colmap -PathType Leaf)
{
    "COLMAP exists at specified path: $colmap"
}
else {
    "COLMAP does not exist at specified path: $colmap"
    "exiting."
    Exit
}

"Extracting features..."
$arguments = 'feature_extractor', "--database_path $database_path", "--image_path $base_images_path"#, '--SiftExtraction.estimate_affine_shape 1', '--SiftExtraction.domain_size_pooling 1'#, '--SiftExtraction.max_image_size 2400'
Start-Process -FilePath $colmap -argumentList $arguments -NoNewWindow -Wait -RedirectStandardOutput $log_path_extraction -RedirectStandardError $log_error_path
"Done."

"Matching features..."
$arguments = 'exhaustive_matcher', "--database_path $database_path"#, '--SiftMatching.min_num_inliers 5'#, --SiftMatching.guided_matching 1'
Start-Process -FilePath $colmap -argumentList $arguments -NoNewWindow -Wait -RedirectStandardOutput $log_path -RedirectStandardError $log_error_path
"Done."

"Mapping..."
$arguments = 'mapper', "--database_path $database_path", "--image_path $base_images_path", "--output_path $sparse_output_path"
Start-Process -FilePath $colmap -argumentList $arguments -NoNewWindow -Wait -RedirectStandardOutput $log_path -RedirectStandardError $log_error_path
"Done."

"Log saved to: $log_path, $log_error_path"