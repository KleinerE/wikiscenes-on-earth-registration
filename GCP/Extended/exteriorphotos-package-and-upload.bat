@echo off

pushd ..\..\Data\Wikiscenes_exterior_images\cathedrals\

if exist %1.7z goto UPLOAD
call "C:\Program Files\7-Zip\7z.exe" a %1.7z %1

:UPLOAD
call gsutil cp %1.7z gs://cwge-test-bucket-0/Wikiscenes_exterior_images/

popd