#!/usr/bin/env python
from math import sqrt,pi, cos, sin, atan2
from random import random
import matplotlib.pyplot as plt
from numpy import linspace

WIDTH = 150
LENGTH = 150
TITLE = 'problem 4'

tic = 8
obstacles=[]
EPSILON = 10
neighborhood = 15
#goals = [(16.5,16.5),(16.5,49.5),(16.5,82.5),(49.5,16.5),(49.5,49.5),(49.5,82.5),(82.5,16.5),(82.5,49.5),(82.5,82.5)]

goals = [(16.5,82.5),(49.5,82.5),(82.5,82.5),(16.5,49.5),(49.5,49.5),(82.5,49.5),(16.5,16.5),(49.5,16.5),(82.5,16.5)]

START_X,START_Y = 150,150 
start = [START_X,START_Y]

GOAL_X, GOAL_Y = 0,50
RADIUS = 6
radius=18


## Import goals

# with open('goals.txt') as data:
#     for l in data:
#         x,y,r = l.split(',')
#         x,y,r = int(x), int(y), float(r)
#         goals.append([x,y,r])

##Define Node Class
class Node:

    def __init__(self, x=0,y=0,parent=None):
        
        self.x = x
        self.y = y
        self.parent = parent

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def distance_to(self, node):
        distance = sqrt((self.x - node.x)**2 + (self.y - node.y)**2)
        return distance
    
    # def closest(self, nodes):
    #     best_distance = self.distance_to(node[0])
    #     best_node = node[0]
    #     for node in nodes:
    #         current_distance = self.distance_to(node)
    #         if current_distance < best_distance:
    #             best_distance = current_distance
    #             best_node = node
    #     print(best_node)
    #     return best_node

    # def closest1(self, nodes):
    #     distances = []
    #     for node in nodes:
    #         distances.append(self.distance_to(node))
    #     min_distance = min(distances)
    #     min_index = distances.index(min_distance)
    #     return nodes[min_index]

    
        
    def closest2(self, nodes):
        return min(nodes, key=self.distance_to)

    def path_to_start(self):
        path = []
        path.append(self)
        current_node = self

        while current_node.parent != None:
            path.append(current_node.parent)
            current_node = current_node.parent
        return path
    def cost_to_start(self):
        path = []
        cost = 0
        path.append(self)
        current_node = self

        while current_node.parent != None:
            path.append(current_node.parent)
            current_node = current_node.parent
        for node in path:
            if  node.parent != None:
                cost += node.distance_to(node.parent)
        return cost

    def cost_to_start_through_node(self,node):
        return node.cost_to_start()+self.distance_to(node)

    def optimal(self,nodes):
        return min(nodes, key=self.cost_to_start_through_node)

def get_goal(tic):
    if tic == 1:
        GOAL_X, GOAL_Y = goals[0]
    elif tic == 2:
        GOAL_X, GOAL_Y = goals[1]
    elif tic == 3:
        GOAL_X, GOAL_Y = goals[2]
    elif tic == 4:
        GOAL_X, GOAL_Y = goals[3]
    elif tic == 5:
        GOAL_X, GOAL_Y = goals[4]
    elif tic == 6:
        GOAL_X, GOAL_Y = goals[5]
    elif tic == 7:
        GOAL_X, GOAL_Y = goals[6]
    elif tic == 8:
        GOAL_X, GOAL_Y = goals[7]
    elif tic == 9:
        GOAL_X, GOAL_Y = goals[8]

    goal = [GOAL_X,GOAL_Y, RADIUS]
    return goal


def collision(new_node,obstacles):
    for i in range(len(obstacles)):
        dist_obs = sqrt(pow(new_node.x-obstacles[i][0],2)+pow(new_node.y-obstacles[i][1],2))
        if dist_obs <= radius+1: #or new_node[0] <= 0 or new_node[0] >= width or new_node[1] <= 0 or new_node[1] >= length:
            collision_flag = 1
            return collision_flag
        # if newnode[0] <= 0 or newnode[0] >= width or newnode[1] <= 0 or newnode[1] >= length:
        #     collision_flag = 1
            #return collision_flag
        else:
            collision_flag = 0



def setup_space(goal):
    figure, ax = plt.subplots(facecolor='white')
    ax.set_ylim((0,LENGTH))
    ax.set_xlim((0,WIDTH))
    plt.xlim()
    plt.ylim()
    plt.title(TITLE)
    ax.set_axis_bgcolor('white')
    start_n = plt.Circle((start[0],start[1]),1, color = 'aqua')
    goal_n = plt.Circle((goal[0],goal[1]),goal[2], color = 'green')
    ax.add_artist(start_n)
    ax.add_artist(goal_n)

    plot_goals = []
    for l in range(len(obstacles)):
        plot_obstacles=plt.Circle((obstacles[l][0],obstacles[l][1]),18,color='black')
        ax.add_artist(plot_obstacles)               
    for k in range(len(goals)):
        plot_goals = plt.Circle((goals[k][0], goals[k][1]), 2, color='red')
        ax.add_artist(plot_goals)
    figure, plt.ion()
    return figure

    
def get_theta_node(new_node, parent):
        theta = atan2(new_node.y-parent.y,new_node.x-parent.x)
        #print('theta is{}'.format(theta))
        return Node(parent.x + EPSILON*cos(theta), parent.y + EPSILON*sin(theta))

def mapping(OldMax, OldMin, NewMax, NewMin, OldValue):
    OldRange = (OldMax - OldMin)  
    NewRange = (NewMax - NewMin)  
    NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin
    return NewValue


def RRT(tic):
    ##Define Initial Parameters
    goal = get_goal(tic)
    figure = setup_space(goal)
    start_node = Node(START_X,START_Y)
    goal_node = Node(goal[0],goal[1])
    current_node = start_node
    figure, plt.plot([0,100], [33, 33], color = 'grey', linewidth = 3)
    figure, plt.plot([0,100], [66, 66], color = 'grey', linewidth = 3)
    figure, plt.plot([33,33], [0, 100], color = 'grey', linewidth = 3)
    figure, plt.plot([66,66], [0, 100], color = 'grey', linewidth = 3)
   # print('Distance to goal is {}'.format(current_node.distance_to(goal_node)))
    nodes = []
    nodes.append(start_node)

    ##Setup plots

    #main loop
    while current_node.distance_to(goal_node) > goal[2]: 
        neighbors = []
        new_node = Node(random()*WIDTH, random()*LENGTH)
        #print(new_node)
        closest_node = new_node.closest2(nodes)
       # print('distance to parent is {}'.format(new_node.distance_to(parent)))
        if new_node.distance_to(closest_node) > EPSILON:
            #print('Too Long')
            new_node = get_theta_node(new_node,closest_node)
            #print('new distance to parent is {}'.format(new_node.distance_to(parent)))
        for node in nodes:
            if node.distance_to(new_node) < neighborhood:
                neighbors.append(node)
        collision_flag=0
        collision_flag=collision(new_node,obstacles)
        if(collision_flag==1):
            continue
        
        best_parent = new_node.optimal(neighbors)
        figure, plt.plot([new_node.x, best_parent.x], [new_node.y, best_parent.y], color = 'blue',linewidth = 2)
        figure, plt.plot([new_node.x, closest_node.x], [new_node.y, closest_node.y], color = 'red',linewidth = 1)
        plt.pause(0.0001)
       
        #current_node = Node(new_node.x, new_node.y, parent = closest_node)
        current_node = Node(new_node.x, new_node.y, parent = best_parent)
        nodes.append(current_node)
        half_way1=((new_node.x+best_parent.x)/2,(new_node.y+best_parent.y)/2)
        half_way2=((new_node.x+closest_node.x)/2,(new_node.y+closest_node.y)/2)
        goal_check1=sqrt(pow(half_way1[0]-goal[0],2)+pow(half_way1[1]-goal[1],2))
        goal_check2=sqrt(pow(half_way2[0]-goal[0],2)+pow(half_way2[1]-goal[1],2))
        if goal_check1<goal[2] or goal_check2<goal[2] :
            break
        #raw_input("hi")
    path = current_node.path_to_start()
    
    final_list = []

    for node in path:
        if node.parent != None:
            new_x = mapping(150, 0, 0.5, 0, node.parent.x)
            new_y = mapping(0, 150, 0.8, 0.4, node.parent.y)
            final_list.append([new_x, new_y])
            figure, plt.plot([node.x, node.parent.x], [node.y, node.parent.y], color = 'cyan')

            ##used to print out coordinates
            #print(node.x, node.y, 0, 0 ,0 ,0)
        else:
            continue  
    new_obstacles=goal
    obstacles.append(new_obstacles)
    return final_list

    # print('Node inside goal is {}'.format(current_node))
    # print(current_node.get_root_node)
    
## Uncomment this to use in terminal

# while True:
#     tic = int(input("Your move? "))
#     RRT(tic)

# RRT_path = RRT(7)
# print RRT_path


# nodes[]
# for i in range(0,9):
#     nodes.append(Node(random()*10, random()*10))

# start = Node(42, 42)
# for i in range(0, 9):
#     new_node = Node(random()*10, random()*10, start)
#     parent = new_node

