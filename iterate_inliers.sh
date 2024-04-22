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
    --cat)
      shift
      if test $# -gt 0; then
        export CAT_NUM=$1
      else
        echo "no category num specified"
        exit 1
      fi
      shift
      ;;
	--stop)
      shift
      if test $# -gt 0; then
        export STOP_IND=$1
      else
        echo "no category num specified"
        exit 1
      fi
      shift
      ;;
	--inc)
      shift
      if test $# -gt 0; then
        export INCREMENT=$1
      fi
      shift
      ;;
	--start)
      shift
      if test $# -gt 0; then
        export START_IND=$1
      fi
      shift
      ;;
    *)
      break
      ;;
  esac
done

# default values for optional parameters.
echo "${INCREMENT:=1}" >> /dev/null
echo "${START_IND:=5}" >> /dev/null

timestamp() {
  date "+%Y-%m-%d %H:%M:%S" # current time
}

mkdir base
mkdir ext

echo "[$(timestamp)]: [${CAT_NUM}] fetching databases from storage bucket..." > log.log 2>&1
gsutil cp gs://cwge-test-bucket-0/inliers_search/${CAT_NUM}/base/database.db ./base/ >> log.log 2>&1
gsutil cp gs://cwge-test-bucket-0/inliers_search/${CAT_NUM}/ext/database.db ./ext/ >> log.log 2>&1
echo "[$(timestamp)]: [${CAT_NUM}] fetch complete." >> log.log 2>&1
sleep 1

mkdir StudioRenders
echo "[$(timestamp)]: [${CAT_NUM}] fetching Google Earth Studio images from storage bucket..." > log.log 2>&1
gsutil cp gs://cwge-test-bucket-0/StudioRenders/${CAT_NUM}.7z . >> log.log 2>&1
sleep 5
7za x -y -bsp0 -bso0 ${CAT_NUM}.7z -oStudioRenders/ >> log.log 2>&1
echo "[$(timestamp)]: [${CAT_NUM}] fetch complete." >> log.log 2>&1
sleep 1
rm -rf ${CAT_NUM}.7z

mkdir WikiScenes_exterior_images
echo "[$(timestamp)]: [${CAT_NUM}] fetching WikiScenes exterior images from storage bucket..." >> log.log 2>&1
gsutil cp gs://cwge-test-bucket-0/WikiScenes_exterior_images/${CAT_NUM}.7z . >> log.log 2>&1
sleep 5
7za x -y -bsp0 -bso0 ${CAT_NUM}.7z -oWikiScenes_exterior_images/ >> log.log 2>&1
echo "[$(timestamp)]: [${CAT_NUM}] fetch complete." >> log.log 2>&1
sleep 1

touch results.csv

for (( i=START_IND; i<=STOP_IND; i+=INCREMENT ))
do
    echo "[$(timestamp)]: inliers: $i" >> log.log
	echo "[$(timestamp)]: base" >> log.log
	echo -n $i, >> results.csv
	mkdir base/sparse_$i
	colmap mapper --log_to_stderr 1 --database_path ./base/database.db --image_path ./StudioRenders/${CAT_NUM}/images/ --output_path ./base/sparse_$i/ --Mapper.min_num_matches $i --Mapper.ignore_watermarks 1 --Mapper.ba_global_images_ratio 20 --Mapper.ba_global_points_ratio 20 --Mapper.ba_global_images_freq 5000 --Mapper.ba_global_points_freq 2500000 --Mapper.ba_global_max_num_iterations 1 --Mapper.ba_global_max_refinements 1 &> colmap.log
	
	export INPUT_DIR=./base/sparse_$i/0/
	if test -d ./base/sparse_$i/1/; then
	 export INPUT_DIR=./base/sparse_$i/1/
	fi
	echo ${INPUT_DIR} >> log.log
	colmap model_analyzer --log_to_stderr 1 --path ${INPUT_DIR} &> ${INPUT_DIR}/analysis.txt
	echo -n "$(sed -n '3p' < ${INPUT_DIR}/analysis.txt | awk '{ print $NF }')", >> results.csv
	
	echo "[$(timestamp)]: ext" >> log.log
	mkdir ext/sparse_$i
	colmap mapper --log_to_stderr 1 --database_path ./ext/database.db --image_path ./WikiScenes_exterior_images/${CAT_NUM}/images_renamed/ --input_path ${INPUT_DIR} --output_path ./ext/sparse_$i/ --Mapper.min_num_matches $i --Mapper.fix_existing_images 1 --Mapper.tri_max_transitivity 3 --Mapper.tri_ignore_two_view_tracks 0 --Mapper.abs_pose_max_error 36 --Mapper.ba_global_max_refinement_change 0.0015 --Mapper.ba_global_images_ratio 20 --Mapper.ba_global_points_ratio 20 --Mapper.ba_global_images_freq 5000 --Mapper.ba_global_points_freq 2500000 --Mapper.ba_global_max_num_iterations 1 --Mapper.ba_global_max_refinements 1 &> colmap.log
	colmap model_analyzer --log_to_stderr 1 --path ./ext/sparse_$i/ &> ./ext/sparse_$i/analysis.txt
	echo "$(sed -n '3p' < ./ext/sparse_$i/analysis.txt | awk '{ print $NF }')", >> results.csv
done

echo "[$(timestamp)]: [${CAT_NUM}] run finished. Sending results to storage bucket and shutting down..." >> log.log 2>&1

gsutil -q cp -r results.csv gs://cwge-test-bucket-0/inliers_search/${CAT_NUM}/ >> log.log 2>&1

sudo shutdown -h now
