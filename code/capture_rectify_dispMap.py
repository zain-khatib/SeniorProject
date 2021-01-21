import cv2,os
import numpy as np

devices = ["http://192.168.43.149:4747/video","http://192.168.43.33:4747/video"]

os.chdir('h:/Senior Project/input')

captures=[cv2.VideoCapture(cam) for cam in devices]

undistortion_map=[None,None]
rectification_map=[None,None]   
    
undistortion_map[0]=np.load('../params/undistortion_map_left.npy')
undistortion_map[1]=np.load('../params/undistortion_map_right.npy')

rectification_map[0]=np.load('../params/rectification_map_left.npy')
rectification_map[1]=np.load('../params/rectification_map_right.npy')

disp_to_depth_mat=np.load('../params/disp_to_depth_mat.npy')

degree=90
rotation_cnt=360/degree

def get_disparity_map(imgL,imgR):
    window_size = 3  # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely

    left_matcher = cv2.StereoSGBM_create(
        minDisparity=-1, # 	Minimum possible disparity value
        numDisparities=5*16,  # max_disp - min_disp has to be dividable by 16 f. E. HH 192, 256
        blockSize=window_size,
        P1=8 * 3 * window_size,
        # wsize default 3; 5; 7 for SGBM reduced size image; 15 for SGBM full size image (1300px and above); 5 Works nicely
        P2=32 * 3 * window_size,
        disp12MaxDiff=12,
        uniquenessRatio=10,
        speckleWindowSize=50,
        speckleRange=32,
        preFilterCap=63,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
    )
    right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
    # FILTER Parameters
    lmbda = 80000
    sigma = 1.3
    visual_multiplier = 6

    # weighted least squares filter
    wls_filter = cv2.ximgproc.createDisparityWLSFilter(matcher_left=left_matcher)
    wls_filter.setLambda(lmbda)

    wls_filter.setSigmaColor(sigma)
    displ = left_matcher.compute(imgL, imgR)  # .astype(np.float32)/16
    dispr = right_matcher.compute(imgR, imgL)  # .astype(np.float32)/16
    displ = np.int16(displ)
    dispr = np.int16(dispr)
    filteredImg = wls_filter.filter(displ, imgL, None, dispr)  # important to put "imgL" here!!!

    filteredImg = cv2.normalize(src=filteredImg, dst=filteredImg, beta=0, alpha=255, norm_type=cv2.NORM_MINMAX);
    filteredImg = np.uint8(filteredImg)

    return filteredImg
    
def create_output(vertices,colors,filename):
    colors=colors.reshape(-1,3)
    vertices=np.hstack([vertices.reshape(-1,3),colors])
    ply_header='''ply
    format ascii 1.0
    element vertex %(vert_num)d
    property float x
    property float y
    property float z
    property uchar red
    property uchar green
    property uchar blue
    end_header
    '''
    with open(filename,'w') as f:
        f.write(ply_header %dict(vert_num=len(vertices)))
        np.savetxt(f,vertices,'%f %f %f %d %d %d')    
    
cnt=0
while(rotation_cnt):
    ret=[False,False]
    [ret[0],left_frame],[ret[1],right_frame]=[cap.read() for cap in captures]
    if not all(ret):
        continue
    rotation_cnt-=1
    cnt+=1
    rectifiedL = cv2.remap(left_frame,undistortion_map[0],rectification_map[0],cv2.INTER_LINEAR)
    rectifiedR = cv2.remap(right_frame,undistortion_map[1],rectification_map[1],cv2.INTER_LINEAR)
    filename=['rect_'+side+'_'+str(cnt)+'.jpg' for side in {'left','right'}]
    cv2.imwrite(filename[0],rectifiedL)
    cv2.imwrite(filename[1],rectifiedR)
    
    disp_map=get_disparity_map(rectifiedL,rectifiedR)
    
    set3Dimages=cv2.reprojectImageTo3D(disp_map,disp_to_depth_mat)
    colors=cv2.cvtColor(disp_map,cv2.COLOR_BGR2RGB)
    create_output(set3Dimages,colors,'../polygons/reconstructed_'+str(cnt)+'.ply')
    