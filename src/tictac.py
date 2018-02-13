import random
from rtica import RRT
from custom import run_plan
import argparse
import struct
import sys
import copy

import rospy
import rospkg


class TTT:
    def __init__(self, playerX, playerO):
        self.grid = [' ']*9
        self.playerX, self.playerO = playerX, playerO
        self.playerX_turn = random.choice([True, False])

    def play_game(self, plot = False):
        self.playerX.start_game('X')
        self.playerO.start_game('O')
        while True: 
            if self.playerX_turn:
                player, char, other_player = self.playerX, 'X', self.playerO
            else:
                player, char, other_player = self.playerO, 'O', self.playerX
            if player.breed == "human":
                self.display_board()
            space = player.move(self.grid)
            if player.breed == "Qlearner" and plot == True:
                path = RRT(space)
                # first = (0.4,0.5)
                path.reverse()
                # path.insert(0,first)
                run_plan(path)
                print path

            if self.grid[space-1] != ' ': 
                player.reward(-99, self.grid) 
                break
            self.grid[space-1] = char
            if self.player_wins(char):
                player.reward(1, self.grid)
                other_player.reward(-1, self.grid)
                break
            if self.board_full(): 
                player.reward(0, self.grid)
                other_player.reward(0, self.grid)
                break
            other_player.reward(0, self.grid)
            self.playerX_turn = not self.playerX_turn

    def player_wins(self, char):
        for a,b,c in [(0,1,2), (3,4,5), (6,7,8),
                      (0,3,6), (1,4,7), (2,5,8),
                      (0,4,8), (2,4,6)]:
            if char == self.grid[a] == self.grid[b] == self.grid[c]:
                return True
        return False

    def board_full(self):
        return not any([space == ' ' for space in self.grid])

    def display_board(self):
        row = " {} | {} | {}"
        hr = "\n-----------\n"
        print((row + hr + row + hr + row).format(*self.grid))


class Player(object):
    def __init__(self):
        self.breed = "human"

    def start_game(self, char):
        print("\nNew game!")

    def move(self, grid):
        return int(input("Your move? "))

    def reward(self, value, grid):
        print("{} rewarded: {}".format(self.breed, value))

    def available_moves(self, grid):
        return [i+1 for i in range(0,9) if grid[i] == ' ']

    

class Q_Learner(Player):
    def __init__(self, epsilon=0.2, alpha=0.3, gamma=0.9):
        self.breed = "Qlearner"
        self.harm_humans = False
        self.q = {} 
        self.epsilon = epsilon 
        self.alpha = alpha 
        self.gamma = gamma 

    def start_game(self, char):
        self.previous_grid = (' ',)*9
        self.last_move = None

    def Q_update(self, state, action):
        if self.q.get((state, action)) is None:
            self.q[(state, action)] = 1.0
        return self.q.get((state, action))

    def move(self, grid):
        self.previous_grid = tuple(grid)
        actions = self.available_moves(grid)

        if random.random() < self.epsilon: 
            self.last_move = random.choice(actions)
            return self.last_move

        qs = [self.Q_update(self.previous_grid, a) for a in actions]
        maxQ = max(qs)

        if qs.count(maxQ) > 1:
            best_options = [i for i in range(len(actions)) if qs[i] == maxQ]
            i = random.choice(best_options)
        else:
            i = qs.index(maxQ)

        self.last_move = actions[i]
        #print('my move was {}'.format(actions[i]))
        return actions[i]

    def reward(self, value, grid):
        if self.last_move:
            self.learn(self.previous_grid, self.last_move, value, tuple(grid))

    def learn(self, state, action, reward, result_state):
        prev = self.Q_update(state, action)
        Qmax = max([self.Q_update(result_state, a) for a in self.available_moves(state)])
        self.q[(state, action)] = prev + self.alpha * ((reward + self.gamma*Qmax) - prev)


player1 = Q_Learner()
player2 = Q_Learner()
for i in range(0,1000):
    t = TTT(player1, player2)
    t.play_game()

player1 = Player()
player2.epsilon = 0

while True:
    t = TTT(player1, player2)
    t.play_game(True)
