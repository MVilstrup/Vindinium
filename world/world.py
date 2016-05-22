'''
@author: Miro Mannino

'''

import random
from constants import (
    CELL_VOID, CELL_MINE, CELL_OWN_MINE, CELL_TAVERN, CELL_HERO_SPAWN,
    CELL_WALL, ACTION_SET, ACTION_EAST, ACTION_WEST, ACTION_NORTH, ACTION_SOUTH,
    ACTION_STAY, PROB_LEFT, PROB_RIGHT, PROB_FORWARD, PROB_BACKWARD, PROB_STAY)
from .reward_calculator import RewardCalulator


class World:

    __cells = None
    size = (0, 0)  #(columns, rows)
    prob = None
    rew = None
    discFactor = 0

    def __init__(self, state, discountFactor=1):
        self.__cells = state.board_map
        self.state = state
        self.size = (len(self.__cells[0]), len(self.__cells))
        self.discFactor = discountFactor
        self.reward_calculator = RewardCalulator(state)

        self.prob = {PROB_FORWARD: 0.3,
                     PROB_LEFT: 0.2,
                     PROB_RIGHT: 0.2,
                     PROB_BACKWARD: 0.2,
                     PROB_STAY: 0.1}

    def transitionFunction(self, position, action):
        ''' this function describes the movements that we can do (deterministic)
            if we are in a wall or a hero cell we can't do anything
            we can't move into a wall
            we can't move out the border of the grid
            returns the new position
        '''
        if action not in ACTION_SET:
            raise Exception("unknown action")
        if self.__cells[position[1]][position[0]] in list(range(1, 5)) + [CELL_WALL]:
            raise Exception("no action allowed")

        if action == ACTION_NORTH:
            ris = (position[0], max(0, position[1] - 1))
        elif action == ACTION_SOUTH:
            ris = (position[0], min(len(self.__cells) - 1, position[1] + 1))
        elif action == ACTION_WEST:
            ris = (max(0, position[0] - 1), position[1])
        else:
            ris = (min(len(self.__cells[0]) - 1, position[0] + 1), position[1])

        if self.__cells[ris[1]][ris[0]] in [CELL_WALL] + list(range(1, 5)):
            return position
        return ris

    def cellTypeAt(self, x, y):
        return self.__cells[y][x]

    def cellAt(self, x, y):
        '''pos is a tuple (x,y)'''
        return self.__cells[y][x]

    def setDiscountFactor(self, df):
        self.discFactor = df

    def setRewards(self,
                   tavern_reward,
                   mine_reward,
                   hero_rewards,
                   void_reward=-0.04):

        self.rew = {CELL_VOID: void_reward,
                    CELL_TAVERN: tavern_reward,
                    CELL_MINE: mine_reward,
                    CELL_OWN_MINE: 0,
                    CELL_HERO_SPAWN: 0,
                    CELL_WALL: 0}

    def possiblePositionsFromAction(self, position, worldAction):
        '''
            given an action worldAction, return a dictionary D,
            where for each action a, D[a] is the probability to do the action a
        '''

        def getProbabilitiesFromAction(worldAction):
            if worldAction in [ACTION_NORTH, ACTION_STAY]:
                return {ACTION_NORTH: self.prob[PROB_FORWARD],
                        ACTION_SOUTH: self.prob[PROB_BACKWARD],
                        ACTION_WEST: self.prob[PROB_LEFT],
                        ACTION_EAST: self.prob[PROB_RIGHT],
                        ACTION_STAY: self.prob[PROB_STAY]}
            elif worldAction == ACTION_SOUTH:
                return {ACTION_NORTH: self.prob[PROB_BACKWARD],
                        ACTION_SOUTH: self.prob[PROB_FORWARD],
                        ACTION_WEST: self.prob[PROB_RIGHT],
                        ACTION_EAST: self.prob[PROB_LEFT],
                        ACTION_STAY: self.prob[PROB_STAY]}
            elif worldAction == ACTION_WEST:
                return {ACTION_NORTH: self.prob[PROB_RIGHT],
                        ACTION_SOUTH: self.prob[PROB_LEFT],
                        ACTION_WEST: self.prob[PROB_FORWARD],
                        ACTION_EAST: self.prob[PROB_BACKWARD],
                        ACTION_STAY: self.prob[PROB_STAY]}
            else:
                return {ACTION_NORTH: self.prob[PROB_LEFT],
                        ACTION_SOUTH: self.prob[PROB_RIGHT],
                        ACTION_WEST: self.prob[PROB_BACKWARD],
                        ACTION_EAST: self.prob[PROB_FORWARD],
                        ACTION_STAY: self.prob[PROB_STAY]}

        if (self.__cells[position[1]][position[0]] in
                list(range(1, 5)) + [CELL_WALL]):
            # We can't do anything in a wall, or in any of the heroes
            return []

        prob = getProbabilitiesFromAction(worldAction)
        result = []
        for a in ACTION_SET:
            result.append((a, self.transitionFunction(position, a), prob[a]))
        return result

    @staticmethod
    def randomAction():
        return ACTION_SET[int(random.random() * 4)]

    def rewardAtCell(self, x, y):
        cell = self.__cells[y][x]
        return self.reward_calculator.get_reward(cell)
