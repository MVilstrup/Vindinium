'''
@author: Miro Mannino

'''

from .world import World
from constants import (CELL_VOID, ACTION_SET, ACTION_NORTH, ACTION_EAST, ACTION_WEST, ACTION_SOUTH, ACTION_STAY)
import math
import time


class Policy:

    valueIterationEepsilon = 0.1
    maxNumberOfIterations = 1000  #for example the maps that have no exits
    _pe_maxk = 50  #for policy evaluation, max number of iteration

    world = None

    numOfIterations = 0
    utilities = None  #memorized as the world grid [y][x]
    policy = None  #created

    def __init__(self, world):
        self.world = world
        self.resetResults()

    def __createEmptyUtilityVector(self):
        '''creates an empty utility vector (that in this case is a matrix), with all number to 0'''
        c, r = self.world.size
        return [[0 for _ in range(c)] for _ in range(r)]

    def resetResults(self):
        self.numOfIterations = 0
        self.utilities = self.__createEmptyUtilityVector()

    def __cellUtility(self, x, y):
        '''calculate the utility of a function using an utilities that is less precise (i.e. using the
			utility vector of the previous step. In the turbo mode it use the current step,
			it leads the computation to end soon)

			this is the Bellman update (see AI: A Modern Approach (Third ed.) pag. 652)
		'''
        if self.world.cellAt(x, y) == CELL_VOID:
            maxSum = None
            for action in ACTION_SET:
                summ = 0
                possibilities = self.world.possiblePositionsFromAction(
                    (x, y), action)
                for _, nextPos, prob in possibilities:
                    summ += prob * self.utilities[nextPos[1]][nextPos[0]]
                if (maxSum is None) or (summ > maxSum): maxSum = summ
            res = self.world.rewardAtCell(x, y) + self.world.discFactor * maxSum
        else:
            #we don't have any action to do, we have only own reward (i.w. V*(s) = R(s) + 0)
            res = self.world.rewardAtCell(x, y)
        return res

    #===========================================================================
    # Policy Iteration
    #===========================================================================

    def __createEmptyPolicy(self):
        '''we create a partial function that is undefined in all points'''
        c, r = self.world.size
        return [[(None if self.world.cellAt(x, y) == CELL_VOID else
                  World.randomAction()) for x in range(c)] for y in range(r)]

    def policyIteration(self, debugCallback=None, turbo=False):
        '''Policy iteration algorithm (see AI: A Modern Approach (Third ed.) pag. 656)

		   the debugCallback must be a function that has three parameters:
				policy: that the function can use to display intermediate results
				isEnded: that the function can use to know if the policyIteration is ended
			the debugCallback must return True, and can stop the algorithm returning False

		   returns the number of iterations it needs to find the fixed point
		'''

        c, r = self.world.size
        policy = self.__createEmptyPolicy()

        reiterate = True
        timeout = time.time() + 0.7
        while (reiterate):
            if time.time() > timeout:
                break

            self.numOfIterations += 1

            self.policyEvaluation(policy, turbo)

            someChanges = False
            for x in range(c):
                for y in range(r):
                    if self.world.cellAt(x, y) == CELL_VOID:
                        newMax = None
                        argMax = None
                        for action in ACTION_SET:
                            summ = 0
                            possibilities = self.world.possiblePositionsFromAction(
                                (x, y), action)
                            for _, nextPos, prob in possibilities:
                                summ += prob * self.utilities[nextPos[1]][
                                    nextPos[0]]
                            if (newMax is None) or (summ > newMax):
                                argMax = action
                                newMax = summ

                        summ = 0
                        possibilities = self.world.possiblePositionsFromAction(
                            (x, y), policy[y][x])
                        for _, nextPos, prob in possibilities:
                            summ += prob * self.utilities[nextPos[1]][nextPos[
                                0]]
                        if newMax > summ:
                            policy[y][x] = argMax
                            someChanges = True

            if debugCallback:
                reiterate = debugCallback(self, False)

            reiterate = someChanges
            if self.numOfIterations >= Policy.maxNumberOfIterations:
                reiterate = False
                print("warning: newMax number of iterations exceeded")

        if debugCallback:
            reiterate = debugCallback(self, True)

        return self.numOfIterations

    def policyEvaluation(self, policy, turbo=False):
        '''Policy Evaluation (see AI: A Modern Approach (Third ed.) pag. 656)
			used by the policy iteration
		'''
        eps = Policy.valueIterationEepsilon
        dfact = self.world.discFactor
        c, r = self.world.size

        if turbo: newUv = self.utilities

        numOfIterations = 0

        reiterate = True
        while (reiterate):
            maxNorm = 0
            numOfIterations += 1

            if not turbo: newUv = self.__createEmptyUtilityVector()

            for x in range(c):
                for y in range(r):
                    newUv[y][x] = self.world.rewardAtCell(x, y)
                    if self.world.cellAt(x, y) == CELL_VOID:
                        action = policy[y][x]

                        possibilities = self.world.possiblePositionsFromAction(
                            (x, y), action)
                        for _, nextPos, prob in possibilities:
                            newUv[y][x] += prob * self.utilities[nextPos[1]][
                                nextPos[0]]
                        newUv[y][x] *= self.world.discFactor
                    maxNorm = max(maxNorm,
                                  abs(self.utilities[y][x] - newUv[y][x]))

            if not turbo: self.utilities = newUv

            if maxNorm <= eps * (1 - dfact) / dfact: reiterate = False
            elif numOfIterations >= Policy._pe_maxk: reiterate = False


    #===========================================================================
    # Other functions
    #===========================================================================
    def get_utility(self, cell, action):
        y, x = cell
        if action == ACTION_NORTH:
            y -= 1
        elif action == ACTION_SOUTH:
            y += 1
        elif action == ACTION_WEST:
            x -= 1
        elif action == ACTION_EAST:
            x += 1

        return self.utilities[y][x]

    def getQValues(self, s, action=None):
        '''calculate the q-value Q(s, a). It is the utility of the state s if we perform the action a
			if action is None it returns a list with the possible q-value for the state s
			for all possible actions.
		'''
        x, y = s

        if self.world.cellAt(x, y) != CELL_VOID: return None

        if action is None:
            res = {}
            for action in ACTION_SET:
                res[action] = self.getQValues(s, action)
        else:

            summ = 0
            possibilities = self.world.possiblePositionsFromAction(
                (x, y), action)
            for _, nextPos, prob in possibilities:
                summ += prob * self.utilities[nextPos[1]][nextPos[0]]
            res = self.world.rewardAtCell(x, y) + self.world.discFactor * summ

        return res

    def getPolicyFromQValues(self, s):
        '''calculate the policy of the state s
			the policy for the state s is the best action to do if you want to have the best possible reward
		'''

        def argmaxQValues(s):
            qv = self.getQValues(s)
            return (max(qv.items(), key=lambda c: c[1])[0] if qv else None)

        return argmaxQValues(s)

    def getPolicyFromUtilityVector(self, s):
        '''calculate the policy of the state s
			the policy for the state s is the best action to do if you want to have the best possible reward
		'''
        x, y = s
        if self.world.cellAt(x, y) != CELL_VOID: return None

        def argmaxValues(s):
            res = {}
            for action in ACTION_SET:
                res[action] = 0
                possibilities = self.world.possiblePositionsFromAction(
                    (x, y), action)
                for _, nextPos, prob in possibilities:
                    res[action] += prob * self.utilities[nextPos[1]][nextPos[0]]
            return (max(res.items(), key=lambda c: c[1])[0] if res else None)

        return argmaxValues(s)

    #===========================================================================
    # String representation
    #===========================================================================

    def utilityVectorToString(self):
        '''utilities string representation'''
        c, r = self.world.size
        util_map = ""
        for row in range(r):
            line = ""
            for col in range(c):
                u = self.utilities[row][col]
                line += " % 2.1f " % u
            util_map += "{}\n".format(line)
        return util_map



    def qValuesToString(self):
        '''qValues string representation'''
        c, r = self.world.size
        ris = ""
        for y in range(r):
            for x in range(c):
                ris += "[ "
                for a in ACTION_SET:
                    v = self.getQValues((x, y), a)
                    if not v is None: ris += "%s : % 2.3f, " % (a, v)
                ris += "] "
            if y < r - 1: ris += "\n"
        return ris

    def policyToString(self):
        '''policy string representation'''
        c, r = self.world.size
        ris = ""
        for y in range(r):
            for x in range(c):
                a = self.getPolicyFromQValues((x, y))
                ris += "_ " if a is None else "%c " % a
            if y < r - 1: ris += "\n"
        return ris
