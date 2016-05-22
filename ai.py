#!/usr/bin/env python
# -*- coding: utf-8 -*-

########################################################################
#
# Pure random A.I, you may NOT use it to win ;-)
#
########################################################################

import random
from world import World, Policy
from threading import Thread
from constants import (ACTION_SET, ACTION_NORTH, ACTION_EAST, ACTION_SOUTH,
                       ACTION_WEST, ACTION_STAY)
from time import sleep


class AI:
    """Pure random A.I, you may NOT use it to win ;-)"""

    def __init__(self):
        self.hero_last_move = None
        self.last_life = None
        self.last_action = None
        self.last_gold = None
        self.last_mine_count = None
        self.last_pos = None
        self.last_nearest_enemy_pos = None
        self.last_nearest_mine_pos = None
        self.last_nearest_tavern_pos = None
        self.last_state = None
        self.current_state = None
        self.round = 0
        self.thread = None

    def process(self, state):
        """Do whatever you need with the state object state"""
        self.last_state = self.current_state
        self.current_state = state
        world = World(state)
        self.policy = Policy(world)
        thread = Thread(target=self.policy.policyIteration)
        thread.deamon = True
        thread.start()
        self.thread = thread

    def available_actions(self):
        y, x = self.current_state.hero.pos
        actions = [ACTION_NORTH, ACTION_EAST, ACTION_SOUTH, ACTION_WEST]
        locations = [(y - 1, x), (y, x + 1), (y + 1, x), (y, x - 1)]

        yield ACTION_STAY
        for index, location in enumerate(locations):
            if location in self.current_state.void:
                yield actions[index]
            elif location in self.current_state.mines:
                yield actions[index]
            elif location in self.current_state.taverns:
                yield actions[index]

    def decide(self):
        dirs = ACTION_SET
        current_location = self.current_state.hero.pos
        actions = []
        sleep(0.5)
        for action in self.available_actions():
            value = self.policy.get_utility(current_location, action)
            actions.append((action, value))
        actions.sort(key=lambda x: x[1], reverse=True)

        print(actions)
        hero_move = actions[0][0]
        print(hero_move)

        return hero_move


if __name__ == "__main__":
    pass
