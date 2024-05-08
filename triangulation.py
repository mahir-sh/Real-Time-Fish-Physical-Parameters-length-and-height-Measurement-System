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
        # set up cameras 
        # ------------------------------

        # cameras variables
        left_camera_source = 2
        right_camera_source = 4
        pixel_width = 640
        pixel_height = 480
        angle_width = 78
        angle_height = 64 # 63
        frame_rate = 20
        camera_separation = 5 + 15/16

        # left camera 1
        ct1 = tt.Camera_Thread()
        ct1.camera_source = left_camera_source
        ct1.camera_width = pixel_width
        ct1.camera_height = pixel_height
        ct1.camera_frame_rate = frame_rate

        # right camera 2
        ct2 = tt.Camera_Thread()
        ct2.camera_source = right_camera_source
        ct2.camera_width = pixel_width
        ct2.camera_height = pixel_height
        ct2.camera_frame_rate = frame_rate

        # camera coding
        #ct1.camera_fourcc = cv2.VideoWriter_fourcc(*"YUYV")
        #ct2.camera_fourcc = cv2.VideoWriter_fourcc(*"YUYV")
        ct1.camera_fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        ct2.camera_fourcc = cv2.VideoWriter_fourcc(*"MJPG")

        # start cameras
        ct1.start()
        ct2.start()

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
        # using default detect values
        targeter1 = tt.Frame_Motion()
        targeter1.contour_min_area = 1
        targeter1.targets_max = 1
        targeter1.target_on_contour = True # False = use box size
        targeter1.target_return_box = False # (x,y,bx,by,bw,bh)
        targeter1.target_return_size = True # (x,y,%frame)
        targeter1.contour_draw = True
        targeter1.contour_box_draw = False
        targeter1.targets_draw = True

        # motion camera2
        # using default detect values
        targeter2 = tt.Frame_Motion()
        targeter2.contour_min_area = 1
        targeter2.targets_max = 1
        targeter2.target_on_contour = True # False = use box size
        targeter2.target_return_box = False # (x,y,bx,by,bw,bh)
        targeter2.target_return_size = True # (x,y,%frame)
        targeter2.contour_draw = True
        targeter2.contour_box_draw = False
        targeter2.targets_draw = True

        # ------------------------------
        # stabilize 
        # ------------------------------

        # pause to stabilize
        time.sleep(0.5)

        # ------------------------------
        # targeting loop 
        # ------------------------------

        # variables
        maxsd = 2 # maximum size difference of targets, percent of frame
        klen  = 3 # length of target queues, positive target frames required to reset set X,Y,Z,D

        # target queues
        x1k,y1k,x2k,y2k = [],[],[],[]
        x1m,y1m,x2m,y2m = 0,0,0,0

        # last positive target
        # from camera baseline midpoint
        X,Y,Z,D = 0,0,0,0

        # loop
        while 1:

            # get frames
            frame1 = ct1.next(black=True,wait=1)
            frame2 = ct2.next(black=True,wait=1)

            # motion detection targets
            targets1 = targeter1.targets(frame1)
            targets2 = targeter2.targets(frame2)

            # check 1: motion in both frames
            if not (targets1 and targets2):
                x1k,y1k,x2k,y2k = [],[],[],[] # reset
            else:

                # split
                x1,y1,s1 = targets1[0]
                x2,y2,s2 = targets2[0]

                # check 2: similar size
                #if 100*(abs(s1-s2)/max(s1,s2)) > minsd:
                if abs(s1-s2) > maxsd:
                    x1k,y1k,x2k,y2k = [],[],[],[] # reset
                else:

                    # update queues
                    x1k.append(x1)
                    y1k.append(y1)
                    x2k.append(x2)
                    y2k.append(y2)

                    # check 3: queues full
                    if len(x1k) >= klen:

                        # trim
                        x1k = x1k[-klen:]
                        y1k = y1k[-klen:]
                        x2k = x2k[-klen:]
                        y2k = y2k[-klen:]

                        # mean values
                        x1m = sum(x1k)/klen
                        y1m = sum(y1k)/klen
                        x2m = sum(x2k)/klen
                        y2m = sum(y2k)/klen
                                
                        # get angles from camera centers
                        xlangle,ylangle = angler.angles_from_center(x1m,y1m,top_left=True,degrees=True)
                        xrangle,yrangle = angler.angles_from_center(x2m,y2m,top_left=True,degrees=True)
                        
                        # triangulate
                        X,Y,Z,D = angler.location(camera_separation,(xlangle,ylangle),(xrangle,yrangle),center=True,degrees=True)
        
            # display camera centers
            angler.frame_add_crosshairs(frame1)
            angler.frame_add_crosshairs(frame2)

            # display coordinate data
            fps1 = int(ct1.current_frame_rate)
            fps2 = int(ct2.current_frame_rate)
            text = 'X: {:3.1f}\nY: {:3.1f}\nZ: {:3.1f}\nD: {:3.1f}\nFPS: {}/{}'.format(X,Y,Z,D,fps1,fps2)
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
            if x1k:
                targeter1.frame_add_crosshairs(frame1,x1m,y1m,48)            
                targeter2.frame_add_crosshairs(frame2,x2m,y2m,48)            

            # display frame
            cv2.imshow("Left Camera 1",frame1)
            cv2.imshow("Right Camera 2",frame2)

            # detect keys
            key = cv2.waitKey(1) & 0xFF
            if cv2.getWindowProperty('Left Camera 1',cv2.WND_PROP_VISIBLE) < 1:
                break
            elif cv2.getWindowProperty('Right Camera 2',cv2.WND_PROP_VISIBLE) < 1:
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

    # close camera2
    try:
        ct2.stop()
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
