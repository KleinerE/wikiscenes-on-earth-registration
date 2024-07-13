param([Int32]$category_index) 

# $base_images_path = ".\StudioRenders\cathedrals\$category_index\images\"
$base_images_path = "..\Data\StudioRenders\cathedrals\$category_index\images\"
# $base_root_path = "..\..\Wikiscenes\base_models\cathedrals\$category_index"
$base_root_path = "..\Models\Base\cathedrals\$category_index"

$base_database_path = "$base_root_path\database.db"
$base_sparse_model_path = "$base_root_path\sparse\0\"

$extended_root_path = "..\Models\extended_test\cathedrals\$category_index"
$extended_images_path = "$extended_root_path\images\"
# $extended_images_path = "..\Data\Wikiscenes_exterior_images\cathedrals\$category_index\images_renamed\"
$extended_images_list_path = "$extended_root_path\images.txt"
$extended_database_path = "$extended_root_path\database.db"
$extended_sparse_output_path = "$extended_root_path\sparse\0\"

$log_path = "$extended_root_path\log_registration.txt"
$log_error_path = "$extended_root_path\log_registration_error.txt"

# md -Force $extended_root_path
# md -Force $extended_images_path
# Copy-item -Force -Recurse -Verbose $sourceDirectory -Destination $destinationDirectory

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

Get-ChildItem $extended_images_path -Name | Out-File -FilePath $extended_images_list_path -Encoding utf8
Copy-Item $base_database_path -Destination $extended_root_path

"Extracting features..."
$arguments = 'feature_extractor', "--database_path $extended_database_path", "--image_path $extended_images_path", "--image_list_path $extended_images_list_path"#, '--SiftExtraction.estimate_affine_shape 1', '--SiftExtraction.domain_size_pooling 1'#, '--SiftExtraction.max_image_size 2400'
Start-Process -FilePath $colmap -argumentList $arguments -NoNewWindow -Wait -RedirectStandardOutput $log_path -RedirectStandardError $log_error_path
"Done."

"Matching features..."
# $arguments = 'exhaustive_matcher', "--database_path $extended_database_path", '--SiftMatching.min_num_inliers 5'#, --SiftMatching.guided_matching 1'
$arguments = 'vocab_tree_matcher', "--database_path $extended_database_path", '--SiftMatching.min_num_inliers 5', "--VocabTreeMatching.vocab_tree_path ..\Data\vocab_tree_flickr100K_words32K.bin"
Start-Process -FilePath $colmap -argumentList $arguments -NoNewWindow -Wait -RedirectStandardOutput $log_path -RedirectStandardError $log_error_path
"Done."

md -Force $extended_sparse_output_path

"Mapping..."
$arguments = 'mapper', "--database_path $extended_database_path", "--image_path $extended_images_path", "--input_path $base_sparse_model_path", "--output_path $extended_sparse_output_path"
Start-Process -FilePath $colmap -argumentList $arguments -NoNewWindow -Wait -RedirectStandardOutput $log_path -RedirectStandardError $log_error_path
"Done."

"Log saved to: $log_path, $log_error_path"