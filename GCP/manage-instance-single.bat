@echo off
@REM set category_num=%1

@REM set dt=%DATE:~6,4%_%DATE:~3,2%_%DATE:~0,2%__%TIME:~0,2%_%TIME:~3,2%_%TIME:~6,2%
@REM set dt=%dt: =0%

echo [%DATE% %TIME%] [%1] Creating instance...
call gcloud compute instances create test-instance-%1 --image=test-image-00 --zone=us-central1-a --machine-type n1-standard-8 --service-account test-service-account-00@analog-mix-408806.iam.gserviceaccount.com --scopes storage-rw >NUL
echo [%DATE% %TIME%] [%1] Instance created: test-instance-%1.

TIMEOUT -T 30 >NUL

echo [%DATE% %TIME%] [%1] Uploading data to instance...
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes instance-work.sh test-instance-%1:. >NUL
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes ..\..\Models\Base\%2\cathedrals\%1\database.db test-instance-%1:. >NUL
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes ..\..\Models\Base\%2\cathedrals\%1\colmap_args.txt test-instance-%1:. >NUL
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes ..\..\Models\Base\%2\cathedrals\%1\log.txt test-instance-%1:. >NUL
echo [%DATE% %TIME%] [%1] Done.

@REM call gcloud compute ssh --zone "us-central1-a" "test-instance-%1" --project "analog-mix-408806" --force-key-file-overwrite -- "chmod +x ./instance-work.sh && nohup ./instance-work.sh -n %1 -t %2"
start /B gcloud compute ssh --quiet --zone "us-central1-a" "test-instance-%1" --project "analog-mix-408806" --force-key-file-overwrite --command="chmod +x ./instance-work.sh && nohup bash ./instance-work.sh -n %1 -t %2 > /dev/null 2>&1 & disown"

@REM mkdir ..\..\Models\Base\%2\cathedrals\%1\result\
@REM call gcloud compute scp --zone "us-central1-a" test-instance-%1:log.txt ..\..\Models\Base\%2cathedrals\%1\result\
@REM call gcloud compute scp --zone "us-central1-a" test-instance-%1:colmap_args.txt ..\..\Models\Base\%2\cathedrals\%1\result\
@REM call gcloud compute scp --zone "us-central1-a" test-instance-%1:analysis.txt ..\..\Models\Base\%2\cathedrals\%1\result\

rem Stop or Delete the Compute Engine Instance
rem call gcloud compute instances stop test-instance-%1
rem or
rem call gcloud compute instances delete test-instance-%1 --zone=us-central1-a --delete-disks=all --quiet