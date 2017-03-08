'''
Created on Mar 8, 2017

@author: richard
'''
from math import sqrt
from cmath import inf

class EvaluationFunction:
    """ Parameterized evaluation function class
    weights consists of six weights used in the evaluation function
    First half of game return w0 * own moves - w1 * opponents moves - w2 * distance from center
    Second half of game return w3 * own moves - w4 * opponents moves - w5 * distance from center
    """
    
    def __init__(self, weights=(1,1,0,1,1,0)):
        self.weights = weights
        
        
        
    def eval_func(self, game, player):
        """Calculate the heuristic value of a game state from the point of view
        of the given player.
    
        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).
    
        player : object
            A player instance in the current game (i.e., an object corresponding to
            one of the player objects `game.__player_1__` or `game.__player_2__`.)
    
        Returns
        -------
        float
            The heuristic value of the current game state to the specified player.
        """
        # TODO: finish this function!
        if game.is_loser(player):
            return float("-inf")
    
        if game.is_winner(player):
            return float("inf")
    
        own_moves = len(game.get_legal_moves(player))
        opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
        if game.move_count < ((game.height * game.width)/2):
            return float(self.weights[0] * own_moves - self.weights[1] * opp_moves - self.weights[2] * __distance_from_center__(game, player))
        else:
            return float(self.weights[3] * own_moves - self.weights[4] * opp_moves - self.weights[5] * __distance_from_center__(game, player))
        
            
            
def __distance_from_center__(game, player):
    """ Calculates the Euclidean distance from the center
    """
    x,y = game.get_player_location(player)
    return sqrt( (x - game.width/2)**2 + (y - game.height/2)**2 )
