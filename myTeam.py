# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

from game import Agent

#Constants
DEFAULTDEPTH=2
POWERCAPSULETIME=80

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
    first = 'RaptorAgent', second = 'RaptorAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class RaptorAgent(CaptureAgent):
  powerTimer=0
  isTimerTracker=True
  def registerInitialState(self,gameState):
    CaptureAgent.registerInitialState(self, gameState) #Pointless comment
    self.inferenceMods = {i:ExactInference(i,self.index,gameState) for i in self.getOpponents(gameState)}
    if self.isTimerTracker:
      self.isTimerTracker=True
      RaptorAgent.isTimerTracker=False
    self.foodNum = 0
    if (not gameState.isOnRedTeam(self.index)):
        RaptorAgent.weights['score']=-abs(RaptorAgent.weights['score'])

  def chooseAction(self,gameState):
    try:
        action = max([(self.evaluate(state,action),action) for state,action in [(gameState.generateSuccessor(self.index,a),a) for a in gameState.getLegalActions(self.index)]])[1]

        if RaptorAgent.powerTimer>0 and self.isTimerTracker:
          RaptorAgent.powerTimer-=2

        if gameState.generateSuccessor(self.index,action).getAgentPosition(self.index) in self.getCapsules(gameState):
          RaptorAgent.powerTimer=POWERCAPSULETIME

        if gameState.generateSuccessor(self.index,action).getAgentPosition(self.index) in self.getFood(gameState).asList():
          self.foodNum+=1

        if self.side(gameState)==0.0:
          self.foodNum=0



        return action
    except Exception:
        return random.choice(gameState.getLegalActions())

  weights={
      'nearestFood':2.0,
      'opponent':1.0,
      'score':800.0,
      'ally':-0.4,
      'nearestPellet':2.0,
      'immediateOpponent':-5000000000.0,
      'isPowered':5000000000.0,
      'isDeadEnd':-100,
      'holdFood':-0.01,
      'dropFood':100,
      'isStop':-100,
      }
  def evaluate(self,gameState,action):
    width, height = gameState.data.layout.width, gameState.data.layout.height
    features={
        'nearestFood':1.0/min(self.getMazeDistance(gameState.getAgentPosition(self.index),p) for p in self.getFood(gameState).asList()),
        'nearestPellet':100.0 if len(self.getCapsules(gameState))==0 else 1.0/min(self.getMazeDistance(gameState.getAgentPosition(self.index),p) for p in self.getCapsules(gameState)),
        'opponent':(1.0/(10*self.powerTimer) if self.isPowered() else 1.0)*self.sideEval(gameState,min([self.inferenceMods[i].getMostLikelyPosition() for i in self.inferenceMods],key=lambda x:self.getMazeDistance(gameState.getAgentPosition(self.index),x)))*1.0/(1+min([self.getMazeDistance(gameState.getAgentPosition(self.index),self.inferenceMods[i].getMostLikelyPosition()) for i in self.inferenceMods])),
        'score': gameState.getScore(),
        'ally': (1.0-self.sideEval(gameState,gameState.getAgentPosition([i for i in self.getTeam(gameState) if i != self.index][0])))*1.0/(1+self.getMazeDistance(gameState.getAgentPosition([i for i in self.getTeam(gameState) if i != self.index][0]),gameState.getAgentPosition(self.index))),
        'immediateOpponent':(0.0 if self.isPowered() else 1.0) * self.side(gameState)*(1.0 if 1.0==util.manhattanDistance(min([self.inferenceMods[i].getMostLikelyPosition() for i in self.inferenceMods],key=lambda x:self.getMazeDistance(gameState.getAgentPosition(self.index),x)),gameState.getAgentPosition(self.index)) else 0.0),
        'isPowered':1.0 if self.isPowered() else 0.0,
        'isDeadEnd':1.0 if len(gameState.getLegalActions(self.index))<=2 else 0.0,
        'holdFood':self.foodNum*(min([self.distancer.getDistance(gameState.getAgentPosition(self.index),p) for p in [(width/2,i) for i in range(1,height) if not gameState.hasWall(width/2,i)]]))*self.side(gameState),
        'dropFood':self.foodNum*(1.0-self.side(gameState)),
        'isStop':1.0 if action==Directions.STOP else 0.0
        }
    for i in self.inferenceMods:
      self.inferenceMods[i].step(gameState)
    return sum([self.weights[i]*features[i] for i in features])

  def sideEval(self,gameState,otherPos):
    width, height = gameState.data.layout.width, gameState.data.layout.height
    if self.index%2==1:
      #red
      if otherPos[0]<width/(2):
        return -1.0
      else:
        return 1.0
    else:
      #blue
      if otherPos[0]>width/2:
        return -1.0
      else:
        return 1.0

  def side(self,gameState):
    width, height = gameState.data.layout.width, gameState.data.layout.height
    pos = gameState.getAgentPosition(self.index)
    if self.index%2==1:
      if pos[0]<width/(2):
        return 1.0
      else:
        return 0.0
    else:
      if pos[0]>width/2-1:
        return 1.0
      else:
        return 0.0

  def isPowered(self):
    return self.powerTimer>0

#class MultiAgentSearchAgent(Agent):
  #def __init__(self, evaluationFunction, depth = '10'):
    #self.evaluationFunction = evaluationFunction
    #self.depth = int(depth)

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on). 

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    ''' 
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py. 
    '''
    CaptureAgent.registerInitialState(self, gameState)

    ''' 
    Your initialization code goes here, if you need any.
    '''
    self.inferenceMods = [ExactInference(i,self.index,gameState) for i in self.getOpponents(gameState)]


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    ''' 
    You should change this in your own agent.
    '''

    for mod in self.inferenceMods:
      mod.step(gameState)
    return actions[0]

class ExactInference:
  def __init__(self, targetIndex,myIndex,gameState):

    #Init beliefs
    self.beliefs = util.Counter()
    width, height = gameState.data.layout.width, gameState.data.layout.height
    for i in range(width):
      for j in range(height):
        self.beliefs[(i,j)]=0.0 if gameState.hasWall(i,j) else 1.0
    self.beliefs.normalize()

    #Initialize targetIndex
    self.targetIndex=targetIndex

    #Initialize my index
    self.index=myIndex

  def getMostLikelyPosition(self):
    return self.beliefs.argMax()

  def step(self,gameState):
    self.elapseTime(gameState)
    self.observe(gameState)

  def observe(self,gameState):
    absPos = gameState.getAgentPosition(self.targetIndex)
    noisyDistance = gameState.getAgentDistances()[self.targetIndex]
    if absPos:
      for pos in self.beliefs:
        self.beliefs[pos]=1.0 if pos == absPos else 0.0
    else:
      for pos in self.beliefs:
        dist = util.manhattanDistance(pos,gameState.getAgentPosition(self.index))
        self.beliefs[pos]*=gameState.getDistanceProb(dist,noisyDistance)
      self.beliefs.normalize()

  def elapseTime(self,gameState):
    newBeliefs = util.Counter()

    for pos in self.beliefs.keys():
      if self.beliefs[pos]>0:
        possiblePositions={}
        x,y=pos
        for dx,dy in ((-1,0),(0,0),(1,0),(0,-1),(0,1)):
          if not gameState.hasWall(x+dx,y+dy):
            possiblePositions[(x+dx,y+dy)]=1
        prob=1.0/len(possiblePositions)
        for possiblePosition in possiblePositions:
          newBeliefs[possiblePosition]+=prob*self.beliefs[pos]
    newBeliefs.normalize()
    self.beliefs=newBeliefs
    if self.beliefs.totalCount()<=0.0:

      width, height = gameState.data.layout.width, gameState.data.layout.height
      for i in range(width):
        for j in range(height):
          self.beliefs[(i,j)]=0.0 if gameState.hasWall(i,j) else 1.0
      self.beliefs.normalize()
