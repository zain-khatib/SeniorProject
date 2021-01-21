import cv2,os
devices = ["http://192.168.43.149:4747/video","http://192.168.43.33:4747/video"]


os.chdir('h:/Senior Project/sample')

captures=[cv2.VideoCapture(cam) for cam in devices]

cnt=0
while (True):
    ret=[False,False]
    
    [ret[0],left_frame],[ret[1],right_frame]=[cap.read() for cap in captures]
   
    if not all(ret):
        continue
    cv2.imshow('left_frame',left_frame)
    cv2.imshow('right_frame',right_frame)
    
    key=cv2.waitKey(1)
    if key == ord('t'):
        #decrease image quality
        cv2.resize(left_frame, (400, 300))
        cv2.resize(right_frame, (400, 300))
        
        #turn image to gray
        gray_left=cv2.cvtColor(left_frame,cv2.COLOR_BGR2GRAY)
        gray_right=cv2.cvtColor(right_frame,cv2.COLOR_BGR2GRAY)
        
        found_chessboard = [False, False]
        found_corners = [None, None]
        chessboard=[None,None]
        
        found_chessboard[0], found_corners[0] = cv2.findChessboardCorners(gray_left, (9,6),None)
        found_chessboard[1], found_corners[1] = cv2.findChessboardCorners(gray_right, (9,6),None)
        
        if all(found_chessboard):
            chessboard[0] = cv2.drawChessboardCorners(left_frame.copy(), (9,6), found_corners[0],found_chessboard[0])
            chessboard[1]=cv2.drawChessboardCorners(right_frame.copy(),(9,6),found_corners[1],found_chessboard[1])
            cv2.imshow('left_frame',chessboard[0])
            cv2.imshow('right_frame',chessboard[1])
            key=cv2.waitKey()
            cnt=cnt+1
            filename=[side+'_'+str(cnt)+'.jpg' for side in {'left','right'}]

            cv2.imwrite(filename[0],left_frame)
            cv2.imwrite(filename[1],right_frame)
        
    if key == ord('q'):
        break
    

[capture.release() for capture in captures]
cv2.destroyAllWindows()

