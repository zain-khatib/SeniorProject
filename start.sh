cd h:/"Senior Project"
#1-using t key you can take photos of chessboard
python code/calibration_images.py

python code/calibrate_cameras.py --rows 9 --columns 6 --input-files "sample" --output-folder "params" --show-chessboards true

python code/capture_rectify_dispMap.py