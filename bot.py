#!/usr/bin/env python
# -*- coding: utf-8 -*-

from world import State
import ai

DIRS = ["North", "East", "South", "West", "Stay"]
ACTIONS = ["Go mine", "Go beer", "Go enemy"]


class Bot:
    """THis is your bot"""

    def __init__(self):
        self.running = True
        self.state = None

        # The A.I, Skynet's rising !
        self.ai = ai.AI()

    def move(self, state):
        """Return store data provided by A.I
        and return selected move"""
        self.state = State(state)

        ################################################################
        # Put your call to AI code here
        ################################################################

        self.ai.process(self.state)
        return self.ai.decide()
