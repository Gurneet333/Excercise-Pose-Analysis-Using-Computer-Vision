import numpy as np
import cv2 as cv
from pose_parser import parse_file, detect_perspective
import time
import math
import pose
from evaluate import evaluate_side_bicepcurl, evaluate_front_bicepcurl


def visualize_front_vid(path):
    video = parse_file(path, False)
    cap = cv.VideoCapture('videos/bicep_8.mp4')

    if(cap.isOpened()==False):
        print("Error")
    i = 0
    initial_frame = i
    start_angle=160
    end_angle = 20
    threshold = 10

    down = False
    up = False
    down_exited = False
    reps = 0
    reps_incorrect = 0

    while (cap.isOpened()):
        ret, image = cap.read()
        frame = video[i]
        # User input
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            break
        if ret==False:
            break
        if(k == 'p'):
            cv.waitKey(0)

        right_upperarm = pose.Part(frame.relbow, frame.rshoulder)
        right_forearm = pose.Part(frame.relbow, frame.rwrist)
        left_upperarm = pose.Part(frame.lelbow, frame.lshoulder)
        left_forearm = pose.Part(frame.lelbow, frame.lwrist)
        torso = pose.Part(frame.neck, frame.mhip)

        #Calculate angles between upperarm and forearm as well as upperarm and torso for both side
        left_angle = left_upperarm.calculate_angle(left_forearm)
        right_angle = right_upperarm.calculate_angle(right_forearm)
        left_upperarm_torso_angle  = left_upperarm.calculate_angle(torso)
        right_upperarm_torso_angle = right_upperarm.calculate_angle(torso)


        #Reps Counter
        #Lower region
        if (start_angle-threshold <= left_angle <= start_angle+threshold):
            down = True
            if (down and down_exited):
                # reps += 1
                down = False
                down_exited = False
                correct, feedback = evaluate_front_bicepcurl(video[initial_frame:i])
                if (correct):
                    reps += 1
                else:
                    reps_incorrect += 1
                initial_frame = i
                print(reps,feedback)

        #Upper region
        if (end_angle-threshold <= left_angle <= end_angle+threshold):
            up = True

        #Downward region exit
        if (down and left_angle<start_angle-threshold):
            down_exited = True

        # Drawing
        cv.putText(image, f"{path} {i}", (250, 20), cv.FONT_HERSHEY_PLAIN,
                   2, (255, 255, 255), 1)
        cv.putText(image, f"Left Angle upperarm forearm: {left_angle}", (10, 50), cv.FONT_HERSHEY_PLAIN,
                   2, (255, 255, 255), 1)
        cv.putText(image, f"Angle upperarm torso: {right_angle}", (10, 80), cv.FONT_HERSHEY_PLAIN,
                   2, (255, 255, 255), 1)
        cv.putText(image, f"Reps: {reps}", (10, 110), cv.FONT_HERSHEY_PLAIN,
                   2, (0, 255, 0), 1)
        cv.putText(image, f"Reps incorrect: {reps_incorrect}", (10, 140), cv.FONT_HERSHEY_PLAIN,
                   2, (0, 0, 255), 1)

        for name, joint in frame:
            x = int(joint.x)
            y = int(joint.y)
            cv.circle(image, (x, y), 5, (0, 0, 255), -1)
            # cv.putText(image, name, (x, y-10), cv.FONT_HERSHEY_SIMPLEX,
            #            0.6, (36, 255, 12), 2)

        # Update
        # time.sleep(0.08)
        i = i+1 
        cv.imshow('Testing', image)
    cv.destroyAllWindows()


    

def visualize_vid(path):
    # Create a black image
    #img = np.zeros((600, 1200, 3), np.uint8)
    # Draw a diagonal blue line with thickness of 5 px
    # cv.line(img, (0, 0), (511, 511), (255, 0, 0), 5)
    # cv.circle(img, (447, 63), 63, (0, 0, 255), -1)
    video = parse_file(path, False)
    side = detect_perspective(video)
    index = 0

    cap = cv.VideoCapture('videos/bicep_6.mp4')
    if(cap.isOpened()==False):
        print("Error")

    i = 0   # to count the frame
    initial_frame = i #start of each reps
    start_angle = 160 #intial position defined
    end_angle = 40 # final position of arm
    threshold = 10 
    down = False #to check whether the arm is in down region
    up = False #to check whether the arm is in upward region
    down_exited = False # to check whether arm exited down region
    reps = 0 # to count the number of reps in exercise
    reps_incorrect = 0 # to counf the incorrect reps
    start = False
    angles = []
    frames_elapsed = 0

    while(cap.isOpened()):
       
        ret, image = cap.read()
        frame = video[i]
        # User input
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            break
        if ret==False:
            break
        if(k == 'p'):
            cv.waitKey(0)

        # Angle
        if (side == pose.Side.right):
            upperarm = pose.Part(frame.relbow, frame.rshoulder)
            forearm = pose.Part(frame.relbow, frame.rwrist)
            torso = pose.Part(frame.rhip, frame.neck)
        else:
            upperarm = pose.Part(frame.lelbow, frame.lshoulder)
            forearm = pose.Part(frame.lelbow, frame.lwrist)
            torso = pose.Part(frame.lhip, frame.neck)
        angle1 = upperarm.calculate_angle(forearm)
        angle2 = upperarm.calculate_angle(torso)
        angles.append(angle1)
        
        #Reps counter
        if (not down_exited and angle1 < start_angle-threshold):
            print(i)
            frames_elapsed = 0
            down_exited = True
        if (down_exited):
            frames_elapsed += 1
        if (start_angle-threshold <= angle1 <= start_angle+threshold):
            if (down_exited and frames_elapsed > 20):
                print(angle1)
                # cv.imwrite("frame%d.jpg" % i, image)
                correct, feedback = evaluate_side_bicepcurl(video[initial_frame:i])
                if (correct):
                    reps += 1
                else:
                    reps_incorrect += 1
                # print(initial_frame,i)
                # print(feedback)
                initial_frame = i
        
                down_exited = False
                frames_elapsed = 0

        # #Lower region
        # if (start_angle-threshold <= angle1 <= start_angle+threshold):
        #     down = True
        #     if (down and down_exited):
        #         # reps += 1
        #         down = False
        #         down_exited = False
        #         start = True
        #         correct, feedback = evaluate_side_bicepcurl(video[initial_frame:i])
        #         if (correct):
        #             reps += 1
        #         else:
        #             reps_incorrect += 1
        #         # print(initial_frame,i)
        #         initial_frame = i
        #         # print(reps,feedback)
        #     # if (down and up):
        #     #     reps += 1
        #     #     final_frame = i
        #     #     down = False
        #     #     up = False
        #     #     feedback = evaluate_bicepcurl (video[initial_frame:final_frame])
        #     #     print(feedback)
        #     #     initial_frame = i

        # # #Upper region
        # # if (end_angle-threshold <= angle1 <= end_angle+threshold):
        # #     up = True

        # #Downward region exit
        # if (down and angle1<start_angle-threshold):
        #     down_exited = True
        # if (start and down and angle1<start_angle-threshold):
        #     # print(i)
        #     print(initial_frame, i)
        #     start = False
        #     index_min = np.argmin(angles[initial_frame:i])+initial_frame
        #     print(initial_frame, index_min)
        #     initial_frame = index_min

        # Drawing
        cv.putText(image, f"{path} {index}", (250, 20), cv.FONT_HERSHEY_PLAIN,
                   2, (255, 255, 255), 1)
        cv.putText(image, f"Angle upperarm forearm: {angle1}", (10, 50), cv.FONT_HERSHEY_PLAIN,
                   2, (255, 255, 255), 1)
        cv.putText(image, f"Angle upperarm torso: {angle2}", (10, 80), cv.FONT_HERSHEY_PLAIN,
                   2, (255, 255, 255), 1)
        cv.putText(image, f"Reps: {reps}", (10, 110), cv.FONT_HERSHEY_PLAIN,
                   2, (0, 255, 0), 1)
        cv.putText(image, f"Reps incorrect: {reps_incorrect}", (10, 140), cv.FONT_HERSHEY_PLAIN,
                   2, (0, 0, 255), 1)

        for name, joint in frame:
            x = int(joint.x)
            y = int(joint.y)
            cv.circle(image, (x, y), 5, (0, 0, 255), -1)
            # cv.putText(image, name, (x, y-10), cv.FONT_HERSHEY_SIMPLEX,
            #            0.6, (36, 255, 12), 2)

        # Update
        # time.sleep(0.04)
        i = i+1 
        cv.imshow('Testing', image)
    cv.destroyAllWindows()


if __name__ == '__main__':
    path = "synthesized/bicep/bicep_good_100.npy"
    # path = "synthesized/bicep/bicep_good_100.npy"
    path = "dataset/front/front_bicep_3.npy"
    # path = "datset/bicep/bicep_good_1.npy"
    # path = "datset/bicep/bicep_bad_1.npy"
    visualize_vid(path)
