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
    -c)
      shift
      if test $# -gt 0; then
        export CAT_NUM=$1
      else
        echo "no category num specified"
        exit 1
      fi
      shift
      ;;
	-n)
      shift
      if test $# -gt 0; then
        export RUN_NAME=$1
      else
        echo "no start time specified"
        exit 1
      fi
      shift
      ;;
	-b)
      shift
      if test $# -gt 0; then
        export BASE_NAME=$1
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

timestamp() {
  date "+%Y-%m-%d %H:%M:%S" # current time
}

echo "[$(timestamp)]: [${CAT_NUM}] fetching WikiScenes exterior images from storage bucket..." > log.log 2>&1
gsutil cp gs://cwge-test-bucket-0/WikiScenes_exterior_images/${CAT_NUM}.7z . >> log.log 2>&1
7za x -y -bsp0 -bso0 ${CAT_NUM}.7z >> log.log 2>&1
echo "[$(timestamp)]: [${CAT_NUM}] fetching base model from storage bucket..." >> log.log 2>&1
mkdir in
gsutil -m cp -r gs://cwge-test-bucket-0/base/${BASE_NAME}/${CAT_NUM}/sparse in/ >> log.log 2>&1
sleep 10
echo "[$(timestamp)]: [${CAT_NUM}] fetch complete." >> log.log 2>&1

#colmap feature_extractor --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --image_path ${CAT_NUM}/images --SiftExtraction.use_gpu 0 &> log.log
#colmap exhaustive_matcher --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --SiftMatching.use_gpu 0 &>> log.log
mkdir -p out/sparse/0 >> log.log 2>&1
echo "[$(timestamp)]: [${CAT_NUM}] running mapper..." >> log.log 2>&1
colmap mapper --log_to_stderr 1 --log_level 1 --database_path database.db --image_path ${CAT_NUM}/images_renamed --input_path in/sparse/0 --output_path out/sparse/0 --Mapper.abs_pose_min_num_inliers 5 &>> colmap_log.txt
echo "colmap mapper --log_to_stderr 1 --log_level 1 --database_path database.db --image_path ${CAT_NUM}/images_renamed --input_path in/sparse/0 --output_path out/sparse/0 --Mapper.abs_pose_min_num_inliers 5" >> colmap_args.txt
echo "[$(timestamp)]: [${CAT_NUM}] mapper finished." >> log.log 2>&1

colmap model_analyzer --log_to_stderr 1 --log_level 1 --path out/sparse/0 &> analysis.txt

7za a -y -bsp0 -bso0 -t7z ${CAT_NUM}_extended.7z out/sparse database.db *.txt >> log.log 2>&1
gsutil -q cp -r ${CAT_NUM}_extended.7z gs://cwge-test-bucket-0/extended/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1
gsutil -q cp -r database.db gs://cwge-test-bucket-0/extended/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1
gsutil -q cp -r out/sparse gs://cwge-test-bucket-0/extended/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1
gsutil -q cp -r *.txt gs://cwge-test-bucket-0/extended/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1

echo "[$(timestamp)]: [${CAT_NUM}] run finished, shutting down and deleting instance..." >> log.log 2>&1

gsutil -q cp -r log.log gs://cwge-test-bucket-0/extended/${RUN_NAME}/${CAT_NUM}/ >/dev/null 2>&1

#gcloud compute instances delete test-instance-${CAT_NUM} --zone=us-central1-a --delete-disks=all --quiet
sudo shutdown -h now