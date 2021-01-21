from argparse import ArgumentParser
from functools import partial
import os

import cv2
from progressbar import ProgressBar, Percentage, Bar
from stereovision.calibration import StereoCalibrator
from stereovision.exceptions import BadBlockMatcherArgumentError

def calibrate_folder(args):
    """
    Calibrate camera based on chessboard images, write results to output folder.

    All images are read from disk. Chessboard points are found and used to
    calibrate the stereo pair. Finally, the calibration is written to the folder
    specified in ``args``.

    ``args`` needs to contain the following fields:
        input_files: List of paths to input files
        rows: Number of rows in chessboard
        columns: Number of columns in chessboard
        square_size: Size of chessboard squares in cm
        output_folder: Folder to write calibration to
    """
    
    input_files=os.listdir(args.input_files)
    for i in range(len(input_files)):
        input_files[i]=os.path.join(args.input_files,input_files[i])
    
    height, width = cv2.imread(input_files[0]).shape[:2]
    calibrator = StereoCalibrator(args.rows, args.columns, args.square_size,
                                  (width, height))
    progress = ProgressBar(maxval=len(input_files),
                          widgets=[Bar("=", "[", "]"),
                          " ", Percentage()])
    print("Reading input files...")
    progress.start()
    while input_files:
        left, right = input_files[:2]
        img_left, im_right = cv2.imread(left), cv2.imread(right)
        calibrator.add_corners((img_left, im_right),
                               show_results=args.show_chessboards)
        input_files = input_files[2:]
        progress.update(progress.maxval - len(input_files))

    progress.finish()
    
    print("Calibrating cameras. This can take a while.")
    calibration = calibrator.calibrate_cameras()
    avg_error = calibrator.check_calibration(calibration)
    print("The average error between chessboard points and their epipolar "
          "lines is \n"
          "{} pixels. This should be as small as possible.".format(avg_error))
    calibration.export(args.output_folder)



if __name__=="__main__":
    #: Command line arguments for collecting information about chessboards
    CHESSBOARD_ARGUMENTS = ArgumentParser(add_help=False)
    CHESSBOARD_ARGUMENTS.add_argument("--rows", type=int,
                                    help="Number of inside corners in the "
                                    "chessboard's rows.", default=9)
    CHESSBOARD_ARGUMENTS.add_argument("--columns", type=int,
                                    help="Number of inside corners in the "
                                    "chessboard's columns.", default=6)
    CHESSBOARD_ARGUMENTS.add_argument("--square-size", help="Size of chessboard "
                                    "squares in cm.", type=float, default=1.8)
    CHESSBOARD_ARGUMENTS.add_argument("--input-files",type=str,help="path to the input folder containing images",required=True)
    CHESSBOARD_ARGUMENTS.add_argument("--output-folder",type=str,help="path to write calibration to",required=True)
    CHESSBOARD_ARGUMENTS.add_argument("--show-chessboards",type=bool,help="show detected corners on chessboard",default=False)
    args=CHESSBOARD_ARGUMENTS.parse_args()
    
    calibrate_folder(args)