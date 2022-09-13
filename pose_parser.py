
import numpy as np
from pose import PoseData, Joint, Side
from typing import List


def parse_single_frame(frame: np.array, normalize: bool = True) -> PoseData:
    if (frame.shape == 18):
        row = np.array([0, 0, 0])
        frame = np.vstack((frame, row))

    joints = [Joint(*joint) for joint in frame]  # Unpack and pass x,y,conf

    joints_clipped = joints[:19]
    pose = (PoseData(*joints_clipped))  # Unpack and pass argument

    if pose.lhip.confidence > 0 and pose.neck.confidence > 0:
        mean_torso = Joint.distance(pose.neck, pose.lhip)
    else:
        mean_torso = Joint.distance(pose.neck, pose.rhip)

    for attr, part in pose:
        setattr(pose, attr, part/mean_torso)
    return pose


def parse_file(file_path: str, normalize: bool = True) -> List[PoseData]:
    frames = np.load(file=file_path)
    pose_sequence = []
    print("Data shape: ", frames.shape)
    # Each frame consists of joint data
    for frame in frames:
        if (frame.shape[0] == 18):
            row = np.array([0, 0, 0])
            frame = np.vstack((frame, row))
        joints = [Joint(*joint) for joint in frame]  # Unpack and pass x,y,conf
        pose_sequence.append(PoseData(*joints))  # Unpack and pass argument

    if (normalize):
        pose_sequence = normalize_pose(pose_sequence)

    return pose_sequence


def save_to_file(file_path: str, pose_sequence: List[PoseData]):
    sequence_arr = []
    for frame in pose_sequence:
        frame_arr = []
        for name, joint in frame:
            frame_arr.append([joint.x, joint.y, joint.confidence])
        sequence_arr.append(frame_arr)
    sequence_arr = np.array(sequence_arr)
    np.save(file_path, sequence_arr)


def normalize_pose(pose_sequence: List[PoseData]) -> List[PoseData]:

    # Normalize pose
    torso_lengths = np.array([Joint.distance(pose.neck, pose.lhip)
                              for pose in pose_sequence if pose.lhip.confidence > 0 and pose.neck.confidence > 0] +
                             [Joint.distance(pose.neck, pose.rhip)
                              for pose in pose_sequence if pose.lhip.confidence > 0 and pose.neck.confidence > 0])
    # print(torso_lengths)
    mean_torso = np.mean(torso_lengths)
    print("Mean torso: ", mean_torso)

    for pose in pose_sequence:
        for attr, part in pose:
            setattr(pose, attr, part/mean_torso)
    return pose_sequence


def detect_perspective(sequence: List[PoseData]) -> Side:
    right_ct, left_ct = 0, 0

    for frame in sequence:
        right_loc = [frame.rshoulder, frame.relbow, frame.rwrist]
        left_loc = [frame.lshoulder, frame.lelbow, frame.lwrist]
        for loc in right_loc:
            right_ct = right_ct + 1 if loc.x > 0 else right_ct
            right_ct = right_ct + 1 if loc.y > 0 else right_ct
        for loc in left_loc:
            left_ct = left_ct + 1 if loc.x > 0 else left_ct
            left_ct = left_ct + 1 if loc.y > 0 else left_ct

    # Check which side has less 0's. Deal with tiebreaking later
    side = Side.right if right_ct > left_ct else Side.left
    print("Primary arm: {}".format(side.value))
    return side


if __name__ == '__main__':
    poseSequence = parse_file('dataset/bicep/bicep_bad_1.npy')
    print(poseSequence[0])
    print(poseSequence[0].lear.x)
