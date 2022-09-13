import os
import sys
import argparse
import time
import cv2

# Import Openpose (Windows/Ubuntu/OSX)
dir_path = os.path.dirname(os.path.realpath(__file__))

# Add the path for dll
## .pyd located at openpose/
## .dll located at openpose/bin/
sys.path.append(dir_path +'\openpose')
os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '\\openpose;' +  dir_path + '\\openpose\\bin;'

import pyopenpose as op

parser = argparse.ArgumentParser()
parser.add_argument("--no_display", default = False)
parser.add_argument("--model_pose", action = 'store', type=str, default="BODY_25")
parser.add_argument("--tracking", action = 'store', type=int, default=1)
parser.add_argument("--number_people_max", action = 'store', type=int, default = 1)

params = dict()
params["model_folder"] = "models/"
params["net_resolution"] = "320x176"
params["face_net_resolution"] = "320x320"
params["render_pose"] = "1"
params["model_pose"] = "BODY_25"
params["tracking"] = "5"
params["number_people_max"] = "1"

args = parser.parse_known_args()
#parse command line argument
# Add others in path?
for i in range(0, len(args[1])):
    curr_item = args[1][i]
    if i != len(args[1])-1: next_item = args[1][i+1]
    else: next_item = "1"
    if "--" in curr_item and "--" in next_item:
        key = curr_item.replace('-','')
        params[key] = "1"
    elif "--" in curr_item and "--" not in next_item:
        key = curr_item.replace('-','')
        params[key] = next_item

#Start OpenPose
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

#Add image path here
path = dir_path + '\\test_data\\test.mkv'


#Capture from path
#cap = cv2.VideoCapture(path)
#Webcam capture
cap = cv2.VideoCapture(0)

if(cap.isOpened() == False):
    print("Error opening Video: ", path)

start = time.time()
total_frame = 0
last_frame = ""
while(True):
    # Create each thread with respective data
    # Datum: The OpenPose Basic Piece of Information Between Threads
    # Datum is one the main OpenPose classes/structs. The workers and threads share by default a
    # std::shared_ptr<std::vector<Datum>>. It contains all the parameters that the different workers and threads need to exchange
    ret, frame = cap.read()
    if ret == True:
        total_frame += 1
        datum = op.Datum()
        #imageToProcess = cv2.imread(imagePath)
        cv2.putText(frame, last_frame, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0)) 
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])
        if not args[0].no_display:
            cv2.imshow("OpenCV", datum.cvOutputData)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        end = time.time()
        if end - start > 1 :
            start = end
            last_frame = "FPS: " + str(total_frame)
            total_frame = 0

cap.release()
cv2.destroyAllWindows()

