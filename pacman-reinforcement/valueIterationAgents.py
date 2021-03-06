# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util
import sys
from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()

        for iteration in range(self.iterations):
            tempvalues = util.Counter()
            for state in states:
                maxvalue = -999999
                actions = self.mdp.getPossibleActions(state)
                for action in actions:
                    transition = self.mdp.getTransitionStatesAndProbs(state, action)
                    sumvalue = 0.0
                    for stateProb in transition:
                        sumvalue += stateProb[1] * (self.mdp.getReward(state, action, stateProb[0]) + self.discount * self.values[stateProb[0]])
                    maxvalue = max(maxvalue, sumvalue)
                if maxvalue != -999999:
                    tempvalues[state] = maxvalue

            for state in states:
                self.values[state] = tempvalues[state]

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        transition = self.mdp.getTransitionStatesAndProbs(state, action)
        value = 0.0
        for stateProb in transition:
            value += stateProb[1] * (self.mdp.getReward(state, action, stateProb[0]) + self.discount * self.values[stateProb[0]])

        return value

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        actions = self.mdp.getPossibleActions(state)
        maxaction = None
        maxvalue = -999999

        for action in actions:
                value = self.computeQValueFromValues(state, action)
                if value > maxvalue:
                    maxvalue = value 
                    maxaction = action
        return maxaction

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()

        for iteration in range(self.iterations):
            state = states[iteration % len(states)]
            if not self.mdp.isTerminal(state):
                self.values[state] = max([self.getQValue(state, action) for action in self.mdp.getPossibleActions(state)])

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        # first we create the initialized variables for our algorithm
        queue = util.PriorityQueue()
        prede = {}

        # for auto grader, we do the iteration on mdp states
        # for every non-terminal state we create the predecessors
        # as the algorithm said
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                for action in self.mdp.getPossibleActions(state):
                    # for every action in our state
                    for stateProb in self.mdp.getTransitionStatesAndProbs(state, action):
                        # if we already had it, then we add the state
                        if stateProb[0] in prede:
                            prede[stateProb[0]].add(state)
                        else: # else we just initialize it
                            prede[stateProb[0]] = {state}
        
        # then for every non-terminal state we calculate the diff 
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                # as said in the algorithm, we will find the max value of Q-values and will calculate the diff
                diff = abs(self.values[state] - max([self.computeQValueFromValues(state, action) for action in self.mdp.getPossibleActions(state)]))
                # then we update the piority queue
                queue.update(state, -diff)
        
        # doing the iteration 
        for iteration in range(self.iterations):
            if queue.isEmpty():
                break
            # getting the state
            state = queue.pop()
            # first we set the init state value
            if not self.mdp.isTerminal(state):
                self.values[state] = max([self.computeQValueFromValues(state, action) for action in self.mdp.getPossibleActions(state)])
            
            # and for the final step
            # we calculate the diff again and then we will update the value
            # if it was more than theta
            for pred in prede[state]:
                if not self.mdp.isTerminal(pred):
                    diff = abs(self.values[pred] - max([self.computeQValueFromValues(pred, action) for action in self.mdp.getPossibleActions(pred)]))
                    if diff > self.theta:
                        queue.update(pred, -diff)
