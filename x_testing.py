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
        # stabilize 
        # ------------------------------

        # pause to stabilize
        time.sleep(0.5)

        # ------------------------------
        # testing area 
        # ------------------------------

        # http://amroamroamro.github.io/mexopencv/opencv/squares_detector_demo.html
        # https://www.askpython.com/python-modules/opencv-filter2d
        

        gblur = 15

        # loop
        while 1:

            # placeholders
            X,Y = 0,0

            # get frames
            frame1 = ct1.next(black=True,wait=1)

            # grayscale
            frame1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)

            # 2D
            frame1 = 

            # blur
            frame1 = cv2.GaussianBlur(frame1,(gblur,gblur),0)
            













            # ------------------------------
            # final frame display 
            # ------------------------------

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

            # display frame
            cv2.imshow("Testing Frame",frame1)

            # detect keys
            key = cv2.waitKey(1) & 0xFF
            if cv2.getWindowProperty('Testing Frame',cv2.WND_PROP_VISIBLE) < 1:
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
    
