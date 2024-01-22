@echo off
@REM %1 = category number
@REM %2 = run name

set VM_NAME=inst-%2-%1
set VM_ZONE=us-central1-a
set VM_TYPE=n1-standard-8
set VM_ACCT=test-service-account-00@analog-mix-408806.iam.gserviceaccount.com

set MODEL_DIR=..\..\Models\Base\%2\cathedrals\%1
set LOG_FILE=%MODEL_DIR%\log.log

echo [%DATE% %TIME%] [%1] Creating instance...
call gcloud compute instances create %VM_NAME% --quiet --image=test-image-00 --zone %VM_ZONE% --machine-type %VM_TYPE% --service-account %VM_ACCT% --scopes storage-rw > %LOG_FILE% 2>&1
TIMEOUT -T 30 >NUL
echo [%DATE% %TIME%] [%1] Instance created: %VM_NAME%.

echo [%DATE% %TIME%] [%1] Uploading data to instance...
call gcloud compute scp --quiet --zone "%VM_ZONE%" --strict-host-key-checking=yes Base\instance-work-base.sh %VM_NAME%:. >> %LOG_FILE% 2>&1
call gcloud compute scp --quiet --zone "%VM_ZONE%" --strict-host-key-checking=yes monitor-mem.sh %VM_NAME%:. >> %LOG_FILE% 2>&1
call gcloud compute scp --quiet --zone "%VM_ZONE%" --strict-host-key-checking=yes %MODEL_DIR%\database.db %VM_NAME%:. >> %LOG_FILE% 2>&1
call gcloud compute scp --quiet --zone "%VM_ZONE%" --strict-host-key-checking=yes %MODEL_DIR%\colmap_args.txt %VM_NAME%:. >> %LOG_FILE% 2>&1
call gcloud compute scp --quiet --zone "%VM_ZONE%" --strict-host-key-checking=yes %MODEL_DIR%\colmap_log.txt %VM_NAME%:. >> %LOG_FILE% 2>&1
echo [%DATE% %TIME%] [%1] Done.

echo [%DATE% %TIME%] [%1] Starting instance work...
start /B gcloud compute ssh --quiet --zone "%VM_ZONE%" "%VM_NAME%" --project "analog-mix-408806" --force-key-file-overwrite --command="chmod +x ./monitor-mem.sh && nohup bash ./monitor-mem.sh -c %1 -n %2 > /dev/null 2>&1 & disown" >NUL
start /B gcloud compute ssh --quiet --zone "%VM_ZONE%" "%VM_NAME%" --project "analog-mix-408806" --force-key-file-overwrite --command="chmod +x ./instance-work-base.sh && nohup bash ./instance-work-base.sh -c %1 -n %2 > /dev/null 2>&1 & disown" >NUL
echo [%DATE% %TIME%] [%1] Done.