#!/usr/bin/env python

"""
Baxter RSDK Inverse Kinematics Pick and Place Demo
"""
import argparse
import struct
import sys
import copy

import rospy
import rospkg

from gazebo_msgs.srv import (
    SpawnModel,
    DeleteModel,
)
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Quaternion,
)

from std_msgs.msg import (
    Header,
    Empty,
)

from baxter_core_msgs.srv import (
    SolvePositionIK,
    SolvePositionIKRequest,
)

import baxter_interface

class PickAndPlace(object):
    def __init__(self, limb, hover_distance = 0.15, verbose=True):
        self._limb_name = limb # string
        self._hover_distance = hover_distance # in meters
        self._verbose = verbose # bool
        self._limb = baxter_interface.Limb(limb)
        self._gripper = baxter_interface.Gripper(limb)
        ns = "ExternalTools/" + limb + "/PositionKinematicsNode/IKService"
        self._iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
        rospy.wait_for_service(ns, 5.0)
        # verify robot is enabled
        print("Getting robot state... ")
        self._rs = baxter_interface.RobotEnable(baxter_interface.CHECK_VERSION)
        self._init_state = self._rs.state().enabled
        print("Enabling robot... ")
        self._rs.enable()

    def move_to_start(self, start_angles=None):
        print("Moving the {0} arm to start pose...".format(self._limb_name))
        if not start_angles:
            start_angles = dict(zip(self._joint_names, [0]*7))
        self._guarded_move_to_joint_position(start_angles)
        self.gripper_open()
        #rospy.sleep(1.0)
        print("Running. Ctrl-c to quit")

    def ik_request(self, pose):
        hdr = Header(stamp=rospy.Time.now(), frame_id='base')
        ikreq = SolvePositionIKRequest()
        ikreq.pose_stamp.append(PoseStamped(header=hdr, pose=pose))
        try:
            resp = self._iksvc(ikreq)
        except (rospy.ServiceException, rospy.ROSException), e:
            rospy.logerr("Service call failed: %s" % (e,))
            return False
        # Check if result valid, and type of seed ultimately used to get solution
        # convert rospy's string representation of uint8[]'s to int's
        resp_seeds = struct.unpack('<%dB' % len(resp.result_type), resp.result_type)
        limb_joints = {}
        if (resp_seeds[0] != resp.RESULT_INVALID):
            seed_str = {
                        ikreq.SEED_USER: 'User Provided Seed',
                        ikreq.SEED_CURRENT: 'Current Joint Angles',
                        ikreq.SEED_NS_MAP: 'Nullspace Setpoints',
                       }.get(resp_seeds[0], 'None')
            if self._verbose:
                print("IK Solution SUCCESS - Valid Joint Solution Found from Seed Type: {0}".format(
                         (seed_str)))
            # Format solution into Limb API-compatible dictionary
            limb_joints = dict(zip(resp.joints[0].name, resp.joints[0].position))
            if self._verbose:
                print("IK Joint Solution:\n{0}".format(limb_joints))
                print("------------------")
        else:
            rospy.logerr("INVALID POSE - No Valid Joint Solution Found.")
            return False
        return limb_joints

    def _guarded_move_to_joint_position(self, joint_angles):
        if joint_angles:
            self._limb.move_to_joint_positions(joint_angles)
        else:
            rospy.logerr("No Joint Angles provided for move_to_joint_positions. Staying put.")

    def gripper_open(self):
        self._gripper.open()
        #rospy.sleep(1.0)

    def gripper_close(self):
        self._gripper.close()
        #rospy.sleep(1.0)

    def _approach(self, pose):
        approach = copy.deepcopy(pose)
        # approach with a pose the hover-distance above the requested pose
        approach.position.z = approach.position.z + self._hover_distance
        joint_angles = self.ik_request(approach)
        self._guarded_move_to_joint_position(joint_angles)

    def _retract(self):
        # retrieve current pose from endpoint
        current_pose = self._limb.endpoint_pose()
        ik_pose = Pose()
        ik_pose.position.x = current_pose['position'].x 
        ik_pose.position.y = current_pose['position'].y 
        ik_pose.position.z = current_pose['position'].z + self._hover_distance
        ik_pose.orientation.x = current_pose['orientation'].x 
        ik_pose.orientation.y = current_pose['orientation'].y 
        ik_pose.orientation.z = current_pose['orientation'].z 
        ik_pose.orientation.w = current_pose['orientation'].w
        joint_angles = self.ik_request(ik_pose)
        # servo up from current pose
        self._guarded_move_to_joint_position(joint_angles)

    def _servo_to_pose(self, pose):
        # servo down to release
        joint_angles = self.ik_request(pose)
        self._guarded_move_to_joint_position(joint_angles)

    def pick(self, pose):
        # open the gripper
        self.gripper_open()
        # servo above pose
        self._approach(pose)
        # servo to pose
        self._servo_to_pose(pose)
        # close gripper
        self.gripper_close()
        # retract to clear object
        self._retract()

    def place(self, pose):
        # servo above pose
        self._approach(pose)
        # servo to pose
        self._servo_to_pose(pose)
        # open the gripper
        self.gripper_open()
        # retract to clear object
        self._retract()


def main():

    rospy.init_node("ik_pick_and_place_demo")

    rospy.wait_for_message("/robot/sim/started", Empty)

    # left_limb = 'left'
    # right_limb = 'right'
    hover_distance = 0.15 # meters
    #Starting Joint angles for left arm

    overhead_orientation = Quaternion(
                             x=-0.0249590815779,
                             y=0.999649402929,
                             z=0.00737916180073,
                             w=0.00486450832011)


    pose1 = Pose(
        position=Point(x=0.4, y=0.0, z=0.05),
        orientation=overhead_orientation)


    pose2 = Pose(
        position=Point(x=0.8, y=0.0, z=0.05),
        orientation=overhead_orientation)

    pose3 = Pose(
        position=Point(x=0.8, y=0.5, z=0.05),
        orientation=overhead_orientation)

    pose4 = Pose(
        position=Point(x=0.4, y=0, z=0.05),
        orientation=overhead_orientation)




    goal1 = Pose(
        position=Point(x=0.4, y=0.0, z=-0.1),
        orientation=overhead_orientation)


    goal2 = Pose(
        position=Point(x=0.8, y=0.0, z=-0.1),
        orientation=overhead_orientation)

    goal3 = Pose(
        position=Point(x=0.8, y=0.5, z=-0.1),
        orientation=overhead_orientation)

    goal4 = Pose(
        position=Point(x=0.4, y=0, z=-0.1),
        orientation=overhead_orientation)




    lstarting_joint_angles = {'left_w0': 0.6699952259595108,
                             'left_w1': 1.030009435085784,
                             'left_w2': -0.4999997247485215,
                             'left_e0': -1.189968899785275,
                             'left_e1': 1.9400238130755056,
                             'left_s0': -0.08000397926829805,
                             'left_s1': -0.9999781166910306}

    rstarting_joint_angles = {'right_w0': 0.6699952259595108,
                             'right_w1': 1.030009435085784,
                             'right_w2': -0.4999997247485215,
                             'right_e0': -1.189968899785275,
                             'right_e1': 1.9400238130755056,
                             'right_s0': -0.08000397926829805,
                             'right_s1': -0.9999781166910306}

    left_arm = PickAndPlace('left', hover_distance)
    right_arm = PickAndPlace('right', hover_distance)

    # left_arm.move_to_start(lstarting_joint_angles)
    # right_arm.move_to_start(rstarting_joint_angles)

    left_arm.move_to_start(lstarting_joint_angles)
    right_arm.move_to_start(rstarting_joint_angles)

    left_arm.gripper_open()
    left_arm._approach(pose3)
    left_arm._servo_to_pose(goal3)
    left_arm.gripper_close()

    # left_arm.move_to_start(lstarting_joint_angles)
    # left_arm.gripper_open()
    # left_arm._approach(pose2)
    # left_arm._servo_to_pose(goal2)
    # left_arm.gripper_close()

    # left_arm.move_to_start(lstarting_joint_angles)
    # left_arm.gripper_open()
    # left_arm._approach(pose3)
    # left_arm._servo_to_pose(goal3)
    # left_arm.gripper_close()

    # left_arm.move_to_start(lstarting_joint_angles)
    # left_arm.gripper_open()
    # left_arm._approach(pose4)
    # left_arm._servo_to_pose(goal4)
    # left_arm.gripper_close()

def run_plan(nodelist):
    rospy.init_node("ik_pick_and_place_demo")
    rospy.wait_for_message("/robot/sim/started", Empty)
    hover_distance = 0.15 

    overhead_orientation = Quaternion(
                             x=-0.0249590815779,
                             y=0.999649402929,
                             z=0.00737916180073,
                             w=0.00486450832011)



    up = Pose(
        position=Point(x = 0.4, y = 0.5, z=0.05),
        orientation=overhead_orientation)

    down = Pose(
        position=Point(x = 0.4, y = 0.5, z=-0.1),
        orientation=overhead_orientation)


    lstarting_joint_angles = {'left_w0': 0.6699952259595108,
                             'left_w1': 1.030009435085784,
                             'left_w2': -0.4999997247485215,
                             'left_e0': -1.189968899785275,
                             'left_e1': 1.9400238130755056,
                             'left_s0': -0.08000397926829805,
                             'left_s1': -0.9999781166910306}

    rstarting_joint_angles = {'right_w0': 0.6699952259595108,
                             'right_w1': 1.030009435085784,
                             'right_w2': -0.4999997247485215,
                             'right_e0': -1.189968899785275,
                             'right_e1': 1.9400238130755056,
                             'right_s0': -0.08000397926829805,
                             'right_s1': -0.9999781166910306}

    left_arm = PickAndPlace('left', hover_distance)
    right_arm = PickAndPlace('right', hover_distance)

    left_arm.move_to_start(lstarting_joint_angles)
    right_arm.move_to_start(rstarting_joint_angles)

    left_arm._servo_to_pose(down)
    left_arm.gripper_close()  
    left_arm._approach(up)


    for i in range(0,len(nodelist)):
        node_x, node_y = nodelist[i]
        print node_x, node_y

        pose = Pose(
            position=Point(x = node_x, y = node_y, z=0.05),
            orientation=overhead_orientation)

        goal = Pose(
            position=Point(x = node_x, y = node_y, z=-0.1),
            orientation=overhead_orientation)

        left_arm._approach(pose)


    up_end = Pose(
        position=Point(x = node_x, y = node_y, z=0.05),
        orientation=overhead_orientation)

    down_end = Pose(
        position=Point(x = node_x, y = node_y, z=-0.1),
        orientation=overhead_orientation)

    left_arm._servo_to_pose(down_end)
    left_arm.gripper_open()  
    left_arm._approach(up_end)

    # if flag == 2:
    #     left_arm.gripper_open()
    #     left_arm._servo_to_pose(down)
    #     left_arm.gripper_close()
    #     left_arm._servo_to_pose(up)
        
    # left_arm._approach(pose)

    # if flag == 1:
    #     left_arm._servo_to_pose(goal)
    #     left_arm.gripper_open()
    


if __name__ == '__main__':
    sys.exit(main())
