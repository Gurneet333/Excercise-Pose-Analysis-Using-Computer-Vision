import argparse
from pose_parser import parse_file
import pose
import numpy as np
import math
from scipy.signal import medfilt

parser = argparse.ArgumentParser()
parser.add_argument('--video', action='store',
                dest='video',
                help='Give video path')
parser.add_argument('--exercise', action= 'store', dest= 'exercise_name', help= 'Exercise name')


results = parser.parse_args()

def main():
    print("Detected exercise: ", results.exercise_name)

    if (results.exercise_name == 'bicep_curl'):
        return _bicep_curl(results.video)
    else:
        print("Invalid argument")
        return False



def _bicep_curl(video):
    frames = parse_file(video)
    
    left_upperarm_forearm_angles = []
    right_upperarm_forearm_angles = []
    left_refer_angles = []
    right_refer_angles = []
    
    dire = ["Upward"]
    for i,frame in enumerate(frames):
        if (i==0):
            initial_position_left = pose.Part(frame.lelbow, frame.lwrist)
            initial_position_right = pose.Part(frame.relbow,frame.rwrist)

        right_upperarm = pose.Part(frame.relbow, frame.rshoulder)
        right_forearm = pose.Part(frame.relbow, frame.rwrist)
        left_upperarm = pose.Part(frame.lelbow, frame.lshoulder)
        left_forearm = pose.Part(frame.lelbow, frame.lwrist)



        left_refer_angle = initial_position_left.calculate_angle(left_forearm)
        right_refer_angle = initial_position_right.calculate_angle(right_forearm)

        left_refer_angles.append(left_refer_angle)
        right_refer_angles.append(right_refer_angle)
        
        left_angle = left_upperarm.calculate_angle(left_forearm)
        right_angle = right_upperarm.calculate_angle(right_forearm)

        

        left_upperarm_forearm_angles.append(left_angle)
        right_upperarm_forearm_angles.append(right_angle)
    
    left_refer_angles = medfilt (left_refer_angles, 11)
    right_refer_angles = medfilt (right_refer_angles, 11)
    
    left_upperarm_forearm_angles= medfilt(left_upperarm_forearm_angles, 11)
    right_upperarm_forearm_angles = medfilt(right_upperarm_forearm_angles,11)
    

    for i in range(1, len(left_refer_angles)):
        prev_angle = left_refer_angles [i-1]
        current_angle = left_refer_angles [i]

        if(current_angle - prev_angle > 0):
            dire.append("Upward")
        elif (current_angle- prev_angle <0):
            dire.append("Downward")
        else:
            dire.append("Stationary")
    feedback = '' 
    reps = 0
    for i in range(1, len(dire)):
        if (dire[i-1]!=dire[i] and dire[i]!=dire[i+1] and dire [i-1]== dire[i+1]):
            dire[i]=dire[i+1]
        if (dire[i] == 'Stationary' and dire[i+1]== "Upward"):
            reps+=1
            print(reps)
            if(left_upperarm_forearm_angles[i]<170.0):
                print("Stretch your arm all the way to bottom")
        if (dire[i] == 'Stationary' and dire[i+1]== "Downward"):
            if (left_upperarm_forearm_angles[i] > 30.0 and left_upperarm_forearm_angles[i]<160.0):
                print("Squeeze your arm all the way to top properly")
            

    print("Total reps:{}".format(reps))

    #Rules
    left_upperarm_forearm_range = np.max(left_upperarm_forearm_angles) - np.min(left_upperarm_forearm_angles)
    right_upperarm_forearm_range = np.max(right_upperarm_forearm_angles) - np.min(right_upperarm_forearm_angles)

    left_upperarm_forearm_minm = np.min(left_upperarm_forearm_angles)
    right_upperarm_forearm_minm = np.min(right_upperarm_forearm_angles)

    print("Left forearm and upperarm range:{}".format(left_upperarm_forearm_range))
    print("Left upperarm and forearm min: {}".format (left_upperarm_forearm_minm))

    print("Right forearm and upperarm range:{}".format(right_upperarm_forearm_range))
    print("Right upperarm and forearm min: {}".format (right_upperarm_forearm_minm))
    
    correct = True
    feedback = ''

    if (left_upperarm_forearm_minm > 30.0):
        correct = False
        feedback+= "Curling not performed all the way to the top"


if __name__== "__main__":
    main()
