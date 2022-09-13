from __future__ import annotations
from typing import List
from dataclasses import dataclass
import numpy as np
import enum

# Class for a single frame of pose data
@dataclass
class PoseData:
    nose: Joint
    neck: Joint
    rshoulder: Joint
    relbow: Joint
    rwrist: Joint
    lshoulder: Joint
    lelbow: Joint
    lwrist: Joint
    mhip: Joint
    rhip: Joint
    rknee: Joint
    rankle: Joint
    lhip: Joint
    lknee: Joint
    lankle: Joint
    reye: Joint
    leye: Joint
    rear: Joint
    lear: Joint
    LBigToe: Joint
    LSmallToe: Joint
    LHeel: Joint
    RBigToe:Joint
    RSmallToe: Joint
    RHeel: Joint

    # JOINT_NAMES = ['nose', 'neck',  'rshoulder', 'relbow', 'rwrist', 'lshoulder', 'lelbow',
    #    'lwrist', 'rhip', 'rknee', 'rankle', 'lhip', 'lknee', 'lankle', 'reye', 'leye', 'rear', 'lear']

    def __str__(self):
        output = []
        for attr, value in self.__dict__.items():
            output.append(
                attr + f" <{value.x}, {value.y}, {value.confidence}>")
        return '\n'.join(output)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def average(self, data):
        blankattr = [0] * 18
        avg_pose = PoseData(*blankattr)
        for tup1, tup2 in zip(self, data):
            name = tup1[0]
            value = tup1[1].average(tup2[1])
            avg_pose.__setattr__(name, value)
        return avg_pose


@dataclass
class Joint:
    x: float
    y: float
    confidence: float

    # Division by scalar
    def __truediv__(self, scalar):
        return Joint(self.x / scalar, self.y / scalar, self.confidence)

    # Distance between two joints
    @staticmethod
    def distance(joint1: Joint, joint2: Joint) -> float:
        return np.sqrt(np.square(joint1.x - joint2.x) + np.square(joint1.y - joint2.y))

    def average(self, joint):
        avg = Joint(0, 0, 0)
        avg.x = (self.x + joint.x)/2.0
        avg.y = (self.y + joint.y)/2.0
        avg.confidence = (self.confidence + joint.confidence)/2.0

        # Special case: While averaging if there is a blank data for joint, make average blank
        if (self.x == 0 or self.y == 0 or joint.x == 0 or joint.y == 0):
            avg.x = 0
            avg.y = 0
        return avg


@dataclass
class Part():
    joint1: Joint
    joint2: Joint

    def get_vector(self):
        return (self.joint2.x - self.joint1.x, self.joint2.y - self.joint1.y)

    def calculate_angle(self, part: Part) -> float:
        vec1 = np.array(self.get_vector())
        vec2 = np.array(part.get_vector())

        # Unit vector conversion
        vec1 = vec1 / np.linalg.norm(vec1)
        vec2 = vec2 / np.linalg.norm(vec2)

        # Cos-1 formula for angle
        angle = np.degrees(
            np.arccos(np.clip(np.sum(np.multiply(vec1, vec2)), -1.0, 1.0)))
        return angle


class Side(enum.Enum):
    left = "Left"
    right = "Right"


class ExerciseType(enum.Enum):
    BICEP_CURL_FRONT = 1
    BICEP_CURL_SIDE = 2
    SHOULDER_PRESS_SIDE = 3

# Helper function to generate part from pose data


def generate_parts(frame: PoseData, side: Side):
    parts = []
    parts.append(Part(frame.nose, frame.neck))

    # Left side
    if side == Side.left:
        parts.append(Part(frame.neck, frame.lshoulder))
        parts.append(Part(frame.lshoulder, frame.lelbow))
        parts.append(Part(frame.lelbow, frame.lwrist))
        parts.append(Part(frame.lhip, frame.lknee))
        parts.append(Part(frame.lknee, frame.lankle))
    # Right side
    elif side == Side.right:
        parts.append(Part(frame.neck, frame.rshoulder))
        parts.append(Part(frame.rshoulder, frame.relbow))
        parts.append(Part(frame.relbow, frame.rwrist))
        parts.append(Part(frame.rhip, frame.rknee))
        parts.append(Part(frame.rknee, frame.rankle))

    return parts


# if __name__ == '__main__':
#     a = PoseData(Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(
#         1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1), Joint(1, 1, 1))
#     from copy import deepcopy
#     b = deepcopy(a)
#     b.nose = Joint(2, 2, 2)
#     c = a.average(b)
#     print(c.nose, c.lear)
