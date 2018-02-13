import random
from RRT_star import RRT
from custom import run_plan
import argparse
import struct
import sys
import copy

import rospy
import rospkg

# rospy.init_node("plan")

#path = RRT(3)
path = RRT(6)
val1, val2 = path[1]

print val1, val2

# first_node = path[0]
# last_node = path[-1]

run_plan(path)