# ------------------------------
# Notice
# ------------------------------

# Copyright 1966 Clayton Darwin claytondarwin@gmail.com

# ------------------------------
# Imports
# ------------------------------

import time
import traceback

import numpy as np
import cv2

import targeting_tools as tt

# ------------------------------
# Testing
# ------------------------------

def run():

    # ------------------------------
    # full error catch 
    # ------------------------------

    try:

        # ------------------------------
        # set up camera 
        # ------------------------------

        # cameras variables
        left_camera_source = 2
        pixel_width = 640
        pixel_height = 480
        angle_width = 78
        angle_height = 64 # 63
        frame_rate = 20

        # camera 1
        ct1 = tt.Camera_Thread()
        ct1.camera_source = left_camera_source
        ct1.camera_width = pixel_width
        ct1.camera_height = pixel_height
        ct1.camera_frame_rate = frame_rate

        # camera coding
        #ct1.camera_fourcc = cv2.VideoWriter_fourcc(*"YUYV")
        ct1.camera_fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        # start camera
        ct1.start()

        # ------------------------------
        # set up angles 
        # ------------------------------

        # cameras are the same, so only 1 needed
        angler = tt.Frame_Angles(pixel_width,pixel_height,angle_width,angle_height)
        angler.build_frame()

        # ------------------------------
        # set up motion detection 
        # ------------------------------

        # motion camera1
        targeter1 = tt.Frame_Motion()
        targeter1.gaussian_blur = 15 # blur (must be positive and odd)
        targeter1.threshold = 15
        targeter1.dilation_value = 6
        targeter1.dilation_kernel = np.ones((targeter1.dilation_value,targeter1.dilation_value),np.uint8)
        targeter1.erosion_iterations = 0
        targeter1.dilation_iterations = 4
        targeter1.contour_min_area = 1  # percent of frame area
        targeter1.contour_max_area = 80 # percent of frame area
        targeter1.targets_max = 5
        targeter1.target_on_contour = True # False = use box size
        targeter1.target_return_box = False # (x,y,bx,by,bw,bh)
        targeter1.target_return_size = True # (x,y,%frame)
        targeter1.contour_draw = True
        targeter1.contour_box_draw = True
        targeter1.targets_draw = 1

        # ------------------------------ 
        # stabilize 
        # ------------------------------

        # pause to stabilize
        time.sleep(0.5)

        # ------------------------------
        # targeting loop 
        # ------------------------------

        # variables
        klen = 1 # length of target queues, positive target frames required to reset set X,Y,Z,D

        # target queues and means = k and m
        x1k,y1k = [],[]
        x1m,y1m = 0,0

        # last positive target
        # from camera baseline midpoint
        # angles
        X,Y = 0,0

        # loop
        while 1:

            # get frames
            frame1 = ct1.next(black=True,wait=1)

            # motion detection targets
            targets1 = targeter1.targets(frame1)

            # check 1: motion
            if not targets1:
                x1k,y1k = [],[] # reset
            else:

                # split
                x1,y1,s1 = targets1[0]
                
                # update queues
                x1k.append(x1)
                y1k.append(y1)

                # check 3: queues full
                if len(x1k) >= klen:

                    # trim
                    x1k = x1k[-klen:]
                    y1k = y1k[-klen:]

                    # mean values
                    x1m = sum(x1k)/klen
                    y1m = sum(y1k)/klen
                            
                    # get angles from camera centers
                    X,Y = xlangle,ylangle = angler.angles_from_center(x1m,y1m,top_left=True,degrees=True)

            # display camera centers
            angler.frame_add_crosshairs(frame1)

            # display coordinate data
            fps1 = int(ct1.current_frame_rate)
            text = 'X: {:3.1f}*\nY: {:3.1f}*\nFPS: {}'.format(X,Y,fps1)
            lineloc = 0
            lineheight = 30
            for t in text.split('\n'):
                lineloc += lineheight
                cv2.putText(frame1,
                            t,
                            (10,lineloc), # location
                            cv2.FONT_HERSHEY_PLAIN, # font
                            #cv2.FONT_HERSHEY_SIMPLEX, # font
                            1.5, # size
                            (0,255,0), # color
                            1, # line width
                            cv2.LINE_AA, #
                            False) #

            # display current target
            if 1:#x1k:
                targeter1.frame_add_crosshairs(frame1,x1m,y1m,48)         

            # display frame
            cv2.imshow("See3Cam",frame1)

            # detect keys
            key = cv2.waitKey(1) & 0xFF
            if cv2.getWindowProperty('See3Cam',cv2.WND_PROP_VISIBLE) < 1:
                break
            elif key == ord('q'):
                break
            elif key != 255:
                print('KEY PRESS:',[chr(key)])

    # ------------------------------
    # full error catch 
    # ------------------------------
    except:
        print(traceback.format_exc())

    # ------------------------------
    # close all
    # ------------------------------

    # close camera1
    try:
        ct1.stop()
    except:
        pass

    # kill frames
    cv2.destroyAllWindows()

    # done
    print('DONE')

# ------------------------------
# run
# ------------------------------

if __name__ == '__main__':
    run()

# ------------------------------
# end
# ------------------------------
    
