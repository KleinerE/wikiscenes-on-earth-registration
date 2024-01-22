@echo off
@REM %1 = category number
@REM %2 = extended run name
@REM %3 = base run name

echo [%DATE% %TIME%] [%1] Creating instance...
call gcloud compute instances create test-instance-%1 --quiet --image=test-image-00 --zone=us-central1-a --machine-type n1-standard-8 --service-account test-service-account-00@analog-mix-408806.iam.gserviceaccount.com --scopes storage-rw > ..\..\Models\Extended\%2\cathedrals\%1\log.log 2>&1
echo [%DATE% %TIME%] [%1] Instance created: test-instance-%1.

TIMEOUT -T 30 >NUL

echo [%DATE% %TIME%] [%1] Uploading data to instance...
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes instance-work-extended.sh test-instance-%1:. >> ..\..\Models\Extended\%2\cathedrals\%1\log.log 2>&1
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes ..\..\Models\Extended\%2\cathedrals\%1\database.db test-instance-%1:. >> ..\..\Models\Extended\%2\cathedrals\%1\log.log 2>&1
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes ..\..\Models\Extended\%2\cathedrals\%1\colmap_args.txt test-instance-%1:. >> ..\..\Models\Extended\%2\cathedrals\%1\log.log 2>&1
call gcloud compute scp --quiet --zone "us-central1-a" --strict-host-key-checking=yes ..\..\Models\Extended\%2\cathedrals\%1\colmap_log.txt test-instance-%1:. >> ..\..\Models\Extended\%2\cathedrals\%1\log.log 2>&1
echo [%DATE% %TIME%] [%1] Done.

echo [%DATE% %TIME%] [%1] Starting instance work...
@REM call gcloud compute ssh --zone "us-central1-a" "test-instance-%1" --project "analog-mix-408806" --force-key-file-overwrite -- "chmod +x ./instance-work.sh && nohup ./instance-work.sh -n %1 -t %2"
start /B gcloud compute ssh --quiet --zone "us-central1-a" "test-instance-%1" --project "analog-mix-408806" --force-key-file-overwrite --command="chmod +x ./instance-work-extended.sh && nohup bash ./instance-work-extended.sh -c %1 -n %2 -b %3 > /dev/null 2>&1 & disown" >NUL
echo [%DATE% %TIME%] [%1] Done.