## Exercise Pose Analysis
This repo contains the analysis section for our final year project entitled: Posture Correction System for Gym Exercises using Computer Vision
## Abstract
Fitness exercises are good for personal health. However doing ‘wrong’ or ineffectively
can be no good and may lead to injury. There are certain exercises that experts want
people to stop due to complications and risk involved in incorrectly performing them.
Exercise mistakes are often introduced when users lack understanding about the pose
and proper form of the exercise.
In our work, we introduce an application that detects the user’s exercise, evaluates their
pose according to the exercise and provides feedback about the exercise along with the
additional feature of exercise tracking at real time. In this way, users can get feedback
from the system and work out accordingly to improve exercise efficiency using the
feedback.
We use OpenPose, a machine learning based solution for robust pose detection which is
used by our system to evaluate the correctness of the exercise based on the rule defined
from various dataset, heuristics and feedback from expert trainers. Our system supports
the evaluation and feedback for common exercises at real time which can greatly enhance the efficiency of learning and improving the common mistakes that occur while
performing the fitness exercise.

## Major libraries
- Matplotlib
- Numpy
- cv2
- tkinter
- Pillow
- OpenPose

## Steps to run
For the final debug output containing calculations of angles and pose estimation plot for bicep curl, run:
```
python debug.py
```

Jupyter notebook files contain the plots for angles, DTW and other evaluation of various exercises.


