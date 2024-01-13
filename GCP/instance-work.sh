#!/bin/bash
while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - attempt to capture frames"
      echo " "
      echo "$package [options] application [arguments]"
      echo " "
      echo "options:"
      echo "-h, --help                show brief help"
      echo "-a, --action=ACTION       specify an action to use"
      echo "-o, --output-dir=DIR      specify a directory to store output in"
      exit 0
      ;;
    -n)
      shift
      if test $# -gt 0; then
        export CAT_NUM=$1
      else
        echo "no process specified"
        exit 1
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done
gsutil cp gs://cwge-test-bucket-0/${CAT_NUM}.7z .
sleep 10
7za x -y ${CAT_NUM}.7z
colmap feature_extractor --database_path ${CAT_NUM}_base_database.db --image_path ${CAT_NUM}/images --SiftExtraction.use_gpu 0 > log.log
colmap exhaustive_matcher --database_path ${CAT_NUM}_base_database.db --SiftMatching.use_gpu 0 >> log.log
mkdir sparse
colmap mapper --database_path ${CAT_NUM}_base_database.db --image_path ${CAT_NUM}/images --output_path sparse/ >> log.log
colmap model_analyzer --path sparse/0 > analysis.log
7za a -t7z ${CAT_NUM}_base.7z sparse log.log analysis.log
gsutil cp ${CAT_NUM}_base.7z gs://cwge-test-bucket-0/
echo successss!