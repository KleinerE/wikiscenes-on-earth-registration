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
        echo "no run name specified"
        exit 1
      fi
      shift
      ;;
	-a)
      shift
      if test $# -gt 0; then
        export MAPPER_ARGS=$1
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

run_mapper() {
	echo "colmap mapper --log_to_stderr 1 --log_level 1 --database_path database.db --image_path ${CAT_NUM}/images --output_path sparse/ ${MAPPER_ARGS}" >> colmap_args.txt
	colmap mapper --log_to_stderr 1 --log_level 1 --database_path database.db --image_path ${CAT_NUM}/images --output_path sparse/ ${MAPPER_ARGS} &>> colmap_log.txt
}

echo "[$(timestamp)]: [${CAT_NUM}] fetching Google Earth Studio images from storage bucket..." > log.log
gsutil cp gs://cwge-test-bucket-0/StudioRenders/${CAT_NUM}.7z . >> log.log 2>&1
sleep 10
7za x -y -bsp0 -bso0 ${CAT_NUM}.7z >> log.log 2>&1
echo "[$(timestamp)]: [${CAT_NUM}] fetch complete." >> log.log 2>&1

#colmap feature_extractor --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --image_path ${CAT_NUM}/images --SiftExtraction.use_gpu 0 &> log.log
#colmap exhaustive_matcher --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --SiftMatching.use_gpu 0 &>> log.log
mkdir sparse >> log.log 2>&1
echo "[$(timestamp)]: [${CAT_NUM}] running mapper..." >> log.log 2>&1
run_mapper
echo "[$(timestamp)]: [${CAT_NUM}] mapper finished." >> log.log 2>&1

colmap model_analyzer --log_to_stderr 1 --log_level 1 --path sparse/0 &> analysis.txt

7za a -y -bsp0 -bso0 -t7z ${CAT_NUM}_base.7z sparse database.db *.txt >> log.log 2>&1
gsutil -q cp -r ${CAT_NUM}_base.7z gs://cwge-test-bucket-0/base/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1
gsutil -q cp -r database.db gs://cwge-test-bucket-0/base/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1
gsutil -q cp -r sparse gs://cwge-test-bucket-0/base/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1
gsutil -q cp -r *.txt gs://cwge-test-bucket-0/base/${RUN_NAME}/${CAT_NUM}/ >> log.log 2>&1

echo "[$(timestamp)]: [${CAT_NUM}] run finished, shutting down and deleting instance..." >> log.log 2>&1

gsutil -q cp -r *.log gs://cwge-test-bucket-0/base/${RUN_NAME}/${CAT_NUM}/ >/dev/null 2>&1

#gcloud compute instances delete test-instance-${CAT_NUM} --zone=us-central1-a --delete-disks=all --quiet
sudo shutdown -h now