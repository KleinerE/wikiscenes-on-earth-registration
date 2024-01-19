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
        echo "no category num specified"
        exit 1
      fi
      shift
      ;;
	-t)
      shift
      if test $# -gt 0; then
        export START_TIME=$1
      else
        echo "no start time specified"
        exit 1
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done

gsutil cp gs://cwge-test-bucket-0/StudioRenders/${CAT_NUM}.7z .
sleep 10
7za x -y ${CAT_NUM}.7z

#colmap feature_extractor --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --image_path ${CAT_NUM}/images --SiftExtraction.use_gpu 0 &> log.log
#colmap exhaustive_matcher --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --SiftMatching.use_gpu 0 &>> log.log
mkdir sparse
colmap mapper --log_to_stderr 1 --log_level 2 --database_path database.db --image_path ${CAT_NUM}/images --output_path sparse/ &>> log.txt
echo "colmap mapper --log_to_stderr 1 --log_level 2 --database_path database.db --image_path ${CAT_NUM}/images --output_path sparse/" >> colmap_args.txt

pidof colmap | xargs -I% grep ^VmPeak /proc/%/status > analysis.txt

colmap model_analyzer --log_to_stderr 1 --log_level 2 --path sparse/0 &>> analysis.txt

7za a -t7z ${CAT_NUM}_base.7z sparse log.txt analysis.txt
gsutil cp -r ${CAT_NUM}_base.7z gs://cwge-test-bucket-0/base/${START_TIME}/
gsutil cp -r sparse gs://cwge-test-bucket-0/base/${START_TIME}/${CAT_NUM}/
gsutil cp -r *.txt gs://cwge-test-bucket-0/base/${START_TIME}/${CAT_NUM}/

echo successss!