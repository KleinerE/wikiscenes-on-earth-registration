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

timestamp() {
  date "+%Y-%m-%d %H:%M:%S" # current time
}

echo "[$(timestamp)]: [${CAT_NUM}] fetching data from storage bucket..."
gsutil -q cp gs://cwge-test-bucket-0/StudioRenders/${CAT_NUM}.7z .
sleep 10
7za x -y -bsp0 -bso0 ${CAT_NUM}.7z
echo "[$(timestamp)]: [${CAT_NUM}] fetch complete."

#colmap feature_extractor --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --image_path ${CAT_NUM}/images --SiftExtraction.use_gpu 0 &> log.log
#colmap exhaustive_matcher --log_to_stderr 1 --log_level 4 --database_path ${CAT_NUM}_base_database.db --SiftMatching.use_gpu 0 &>> log.log
mkdir sparse
echo "[$(timestamp)]: [${CAT_NUM}] running mapper..."
colmap mapper --log_to_stderr 1 --log_level 1 --database_path database.db --image_path ${CAT_NUM}/images --output_path sparse/ &>> log.txt
echo "colmap mapper --log_to_stderr 1 --log_level 1 --database_path database.db --image_path ${CAT_NUM}/images --output_path sparse/" >> colmap_args.txt
echo "[$(timestamp)]: [${CAT_NUM}] mapper finished."

colmap model_analyzer --log_to_stderr 1 --log_level 1 --path sparse/0 &> analysis.txt

7za a -y -bsp0 -bso0 -t7z ${CAT_NUM}_base.7z sparse log.txt analysis.txt colmap_args.txt
gsutil -q cp -r ${CAT_NUM}_base.7z gs://cwge-test-bucket-0/base/${START_TIME}/
gsutil -q cp -r sparse gs://cwge-test-bucket-0/base/${START_TIME}/${CAT_NUM}/
gsutil -q cp -r *.txt gs://cwge-test-bucket-0/base/${START_TIME}/${CAT_NUM}/

echo "[$(timestamp)]: [${CAT_NUM}] run finished, shutting down and deleting instance..."

#gcloud compute instances delete test-instance-${CAT_NUM} --zone=us-central1-a --delete-disks=all --quiet