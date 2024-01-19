@REM set category_num=%1

@REM set dt=%DATE:~6,4%_%DATE:~3,2%_%DATE:~0,2%__%TIME:~0,2%_%TIME:~3,2%_%TIME:~6,2%
@REM set dt=%dt: =0%

call gcloud compute instances create test-instance-%1 --image=test-image-00 --zone=us-central1-a --machine-type n1-standard-8 --service-account test-service-account-00@analog-mix-408806.iam.gserviceaccount.com --scopes storage-rw
TIMEOUT -T 30

call gcloud compute scp --zone "us-central1-a" instance-work.sh test-instance-%1:.
call gcloud compute scp --zone "us-central1-a" ..\..\Models\Base\%2\cathedrals\%1\database.db test-instance-%1:.
call gcloud compute scp --zone "us-central1-a" ..\..\Models\Base\%2\cathedrals\%1\colmap_args.txt test-instance-%1:.
call gcloud compute scp --zone "us-central1-a" ..\..\Models\Base\%2\cathedrals\%1\log.txt test-instance-%1:.

call gcloud compute ssh --zone "us-central1-a" "test-instance-%1" --project "analog-mix-408806" --force-key-file-overwrite --command="chmod +x instance-work.sh && bash instance-work.sh -n %1 -t %2"

mkdir ..\..\Models\Base\%2\cathedrals\%1\
call gcloud compute scp --zone "us-central1-a" test-instance-%1:log.txt ..\..\Models\Base\%2cathedrals\%1\
call gcloud compute scp --zone "us-central1-a" test-instance-%1:colmap_args.txt ..\..\Models\Base\%2\cathedrals\%1\
call gcloud compute scp --zone "us-central1-a" test-instance-%1:analysis.txt ..\..\Models\Base\%2\cathedrals\%1\

rem Stop or Delete the Compute Engine Instance
call gcloud compute instances stop test-instance-%1
rem or
rem call gcloud compute instances delete test-instance-%1 --zone=us-central1-a --delete-disks=all --quiet