from __future__ import annotations
import cv2
import pose_parser as parser
import numpy as np
import time
import pose
from evaluate import evaluate_side_bicepcurl
from datetime import datetime



from tkinter import *
# import tkinter as tk
from PIL import Image as IMAGE
from PIL import ImageTk
from os import listdir

# Global Constant
cv_default_font = cv2.FONT_HERSHEY_PLAIN
font_size = 1
root_dir = "./demo/data/"

# List all file under root directory
files = listdir(root_dir)
active_file = files[0]
frame_index = 0

# initialize tkinter
root = Tk()
# root.geometry("1080x640") #custom code
variable = StringVar(root)
variable.set(active_file)
image_frame = Label(root)
image_frame.grid(row=1, column=0)

# Initializations for debugging variables
cap = cv2.VideoCapture(f'demo/video/{active_file.split(".")[0]}.mp4')

if(cap.isOpened() == False):
    print("Error")


initial_frame = 0  # start of each reps
start_angle = 160  # intial position defined
end_angle = 40  # final position of arm
threshold = 10
down = False  # to check whether the arm is in down region
down_exited = False  # to check whether arm exited down region
reps = 0  # to count the number of reps in exercise
reps_incorrect = 0  # to counf the incorrect reps
frames_elapsed = 0
feedback = ""
feedback2=""
feedback3=""


# file change callback


def on_file_change(*args):
    global video, side, active_file, cap, initial_frame, start_angle, end_angle, threshold, down, down_exited, frame_index
    global reps, reps_incorrect, frames_elapsed, feedback, frame_index,feedback2,feedback3
    active_file = variable.get()
    video = parser.parse_file(root_dir + '/' + active_file, False)
    cap.release()
    cap = cv2.VideoCapture(f'demo/video/{active_file.split(".")[0]}.mp4')
    if(cap.isOpened() == False):
        print("Error")
    initial_frame = 0  # start of each reps
    start_angle = 160  # intial position defined
    end_angle = 40  # final position of arm
    threshold = 10
    down = False  # to check whether the arm is in down region
    down_exited = False  # to check whether arm exited down region
    reps = 0  # to count the number of reps in exercise
    reps_incorrect = 0  # to counf the incorrect reps
    frames_elapsed = 0
    feedback = ""
    feedback2=""
    feedback3=""

    frame_index = 0
    side = parser.detect_perspective(video)
    root.title(active_file)
    print(active_file)


# Attach callback
variable.trace("w", on_file_change)
on_file_change(())


###################################################################

def evaluate_angle_per_frame(frame, side):
    # Angles to calculate
    upperarm_forearm_angles = []
    upperarm_torso_angles = []
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
    upperarm_forearm_angles.append(angle1)
    upperarm_torso_angles.append(angle2)
    frame_out = {}
    # Upper angle
    frame_out["a1"] = angle1
    frame_out["a2"] = angle2
    return frame_out

#############################################################


def debugVideo():
    # Main call every frame
    global start_angle, end_angle, threshold, frame_index, down_exited, frames_elapsed, initial_frame, reps, reps_incorrect
    global is_playing, feedback,feedback2,feedback3, delay
    color = (0, 255, 0)
    ret, img = cap.read()
    if ret == False:
        return
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Get necessary elements
    frame = video[frame_index]
    # Evaluate output for frame
    output = evaluate_angle_per_frame(frame, side)
    angle1 = output["a1"]
    angle2 = output["a2"]

    ################# Reps counter and feedback logic ###########################
    if (not down_exited and angle1 < start_angle-threshold):
        frames_elapsed = 0
        down_exited = True
    if (down_exited):
        frames_elapsed += 1
    if (start_angle-threshold <= angle1 <= start_angle+threshold):
        if (down_exited and frames_elapsed > 20):
            print(angle1)
            # cv.imwrite("frame%d.jpg" % i, image)
            correct, feedback, feedback2, feedback3 = evaluate_side_bicepcurl(
                video[initial_frame:frame_index])
            if (correct):
                reps += 1
            else:
                reps_incorrect += 1
            # print(initial_frame,i)
            # print(feedback)
            with open('feedback.txt', 'a') as f:
                # datetime object containing current date and time
                now = datetime.now()

                # dd/mm/YY H:M:S
                dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
                f.writelines(f"date and time =  {dt_string} \n \n")
                f.writelines(f'Repetition : {reps+reps_incorrect} \n')
                if(correct):
                    f.writelines("Correct Repetition. \n")
                    # f.writelines(f'{feedback} \n')
                    f.writelines(f'{feedback2} \n \n')
                    # f.writelines(f'{feedback3} \n')
                else:
                    f.writelines(f'Incorrect Repetition. \n')
                    # f.writelines(f'{feedback} \n')
                    f.writelines(f'Feedback:  {feedback2} \n')
                    f.writelines(f'{feedback3} \n \n \n')
                    
                
            initial_frame = frame_index

            down_exited = False
            frames_elapsed = 0

    #### Rendering part ############################################################
    # Generate part for this frame
    parts = pose.generate_parts(frame, side)

    # Expected line
    # Given a line AB, we need to find D and E at an angle
    def getCoordAtAnAngle(aX, aY, bX, bY, length, angle):
        vX = bX-aX
        vY = bY-aY
        #print(str(vX)+" "+str(vY))
        if(vX == 0 or vY == 0):
            return 0, 0, 0, 0
        mag = np.sqrt(vX*vX + vY*vY)
        vX = vX / mag
        vY = vY / mag

        tempX = vX
        tempY = vY
        vX = tempX*np.cos(angle) - tempY*np.sin(angle)
        vY = tempX*np.sin(angle) + tempY*np.cos(angle)

        cX = bX + vX * length
        cY = bY + vY * length
        dX = bX - vX * length
        dY = bY - vY * length
        return int(cX), int(cY), int(dX), int(dY)
    test = parts[2]
    x1, y1, x2, y2 = getCoordAtAnAngle(test.joint1.x, test.joint1.y,
                                       test.joint2.x, test.joint2.y, 100, np.deg2rad(140))
    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Draw debug info
    # Parts
    for part in parts:
        joint1 = part.joint1
        joint2 = part.joint2
        if (joint1.x == 0 or joint1.y == 0 or joint2.x == 0 or joint2.y == 0):
            continue
        cv2.line(img, (int(joint1.x), int(joint1.y)),
                 (int(joint2.x), int(joint2.y)), color, 2)
    # Keypoints
    for name, joint in frame:
        x = int(joint.x)
        y = int(joint.y)
        if(x == 0 or y == 0):
            continue
        if (side == pose.Side.right and name[0] == 'l') or (side == pose.Side.left and name[0] == 'r'):
            continue

        cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
        cv2.putText(img, name, (x, y + 10), cv_default_font,
                    0.8, (36, 255, 12), font_size)

    # Display current frame information
    textcolor = (255, 255, 0)
    cv2.rectangle(img, (0, 0), (710, 180), (0, 0, 0), -1)
    cv2.putText(img, f"Frame: {frame_index}", (10, 10),
                cv_default_font, 0.8, textcolor, font_size)
    cv2.putText(img, f"Side: {side}", (10, 30),
                cv_default_font, 0.8, textcolor, font_size)
    cv2.putText(img, f"Angle upper and forearm: {round(output['a1'],2)}", (
        10, 50), cv_default_font, 0.8, textcolor, font_size)
    cv2.putText(img, f"Angle upper arm and torso: {round(output['a2'],2)}", (
        10, 70), cv_default_font, 0.8, textcolor, font_size)
    # cv2.putText(img, f"Correct: {output['status']}", (10, 100), cv_default_font, 1, (0,0,0), font_size)
    textcolor = (0, 255, 0)
    cv2.putText(img, f"Reps correct: {reps}", (10, 90), cv_default_font,
                0.8, textcolor, 1)
    textcolor = (255, 0, 0)
    cv2.putText(img, f"Reps incorrect: {reps_incorrect}", (10, 110), cv_default_font,
                0.8, textcolor, 1)
    textcolor = (255, 255, 255)
    cv2.putText(img, f"{feedback}", (10, 130), cv_default_font,
                0.8,textcolor, 1)
    cv2.putText(img, f"Feedback: {feedback2}", (10, 150), cv_default_font,
                0.8, textcolor, 1)
    cv2.putText(img, f"{feedback3}", (10, 170), cv_default_font,
                0.8, textcolor, 1)
    
    


    

    ###########Updates###############################################
    # Display current frame
    frame_index = (frame_index + 1) % len(video)

    final_image = ImageTk.PhotoImage(IMAGE.fromarray(img))
    image_frame.configure(image=final_image)
    image_frame.image = final_image

    # root.after(10, debugVideo)
    if (is_playing):
        root.after(delay, debugVideo)
    else:
        root.after_cancel(debugVideo)

#####################################################################################


##########Remaining GUI controls########################################
def play_callback(root):
    global is_playing
    is_playing = not is_playing
    root.after(10, debugVideo)


def set_delay(val):
    global delay
    delay = val


is_playing = True
delay = 10
btn = Button(root, text='Play/Pause',
             command=lambda: play_callback(root))
btn.grid(row=0, column=0, padx=10, pady=10, sticky="W")

file_selector = OptionMenu(root, variable, *files)
file_selector.grid(row=0, column=0, padx=10, pady=10, sticky="E")

scale = Scale(orient='horizontal', from_=1,
              to=100, command=set_delay)
scale.grid(row=0, column=0, padx=1, pady=1, sticky="N")
scale.set(delay)


# Main call
root.after(delay, debugVideo)
root.mainloop()
