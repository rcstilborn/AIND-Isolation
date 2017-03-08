"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random
import logging
from cmath import inf
from math import sqrt

logging.basicConfig(level=logging.ERROR)

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

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

    return __heuristic1__(game, player)
    
def __heuristic1__(game, player):
    """ Aggressive in the first half, 'normal' in the second half
    """
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    if game.move_count < ((game.height * game.width)/2):
        return float(own_moves - 3 * opp_moves)
    else:
        return float(own_moves - opp_moves)

def __heuristic2__(game, player):
    """ Moderately aggressive for the whole game
    """
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - 2 * opp_moves)

def __heuristic3__(game, player):
    """ Tries to stay close to the center of the board for the first half of the game
    """
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    if game.move_count < ((game.height * game.width)/2):
        return float(own_moves - opp_moves - __distance_from_center__(game, player))
    else:
        return float(own_moves - opp_moves)

def __distance_from_center__(game, player):
    """ Calculates the Euclidean distance from the center
    """
    x,y = game.get_player_location(player)
    return sqrt( (x - game.width/2)**2 + (y - game.height/2)**2 )


def paramterized_heuristic(game, player):
    """ Assumes the following parameter.
    """
    pass


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.best_move_so_far = (-1, -1)
        
    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        logging.debug("get_move - legal moves: %s", str(legal_moves))
        
        self.time_left = time_left


        # TODO: finish this function!

        # Check if we have any legal moves
        if not legal_moves:
            return (-1, -1)

        # Let's set best move so far to be the first legal move so we always 
        # have something to return in case of timeout
        self.best_move_so_far = legal_moves[0]
        
         
        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            if self.iterative:
                it = 1
                while True:
                    if self.method == 'minimax':
                        _, self.best_move_so_far = self.minimax(game, it)
                    else:
                        _, self.best_move_so_far = self.alphabeta(game, it)
                    it += 1
            else:    
                if self.method == 'minimax':
                    _, self.best_move_so_far = self.minimax(game, self.search_depth)
                else:
                    _, self.best_move_so_far = self.alphabeta(game, self.search_depth)

        except Timeout:
            # Handle any actions required at timeout, if necessary
            logging.debug("Time is up - get_move returning: %s", str(self.best_move_so_far))
            return self.best_move_so_far

        # Return the best move from the last completed search iteration
        logging.debug("get_move returning: %s", str(self.best_move_so_far))

        return self.best_move_so_far

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """

        #logging.debug("minimax(%d, %s)", depth, maximizing_player)

        # If we are out of time then jump out
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()      
        

        if depth <= 0:  # Last row to search so return score of this board
            return self.score(game, self),(-1,-1)
        
        # Otherwise search the next layer
        legal_moves = game.get_legal_moves()
        #logging.debug("    Found %d legal moves: %s", len(legal_moves), str(legal_moves))
        
        # Check for some legal moves - if none return score of this board
        if len(legal_moves) == 0:
            return self.score(game, self),(-1,-1)

        results = []
        for m in legal_moves:
            #logging.debug("  Trying this move: %s", str(m))
            score, _ = self.minimax(game.forecast_move(m), depth-1, not maximizing_player)
            results.append((score,m))
                                       
        #results = [(score,_=self.minimax(game.forecast_move(m), depth-1, not maximizing_player)[0], m) for m in legal_moves]
        #logging.debug("    Got these results: %s", str(results))
        
        if maximizing_player:
            #logging.debug("    Returning: %s", max(results))
            return max(results)
        else:
            #logging.debug("    Returning: %s", min(results))
            return min(results)
        

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project unit tests; you cannot call any other
                evaluation function directly.
        """
        #logging.debug("alphabeta(%d, %f, %f, %s)", depth, alpha, beta, maximizing_player)

        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        if depth <= 0:  # last row to search so return score of this board
            score = self.score(game, self)
            #logging.debug("  Returning %f", score)
            return score,(-1,-1)
      
        # Otherwise search the next layer
        legal_moves = game.get_legal_moves()
        #logging.debug("Found %d legal moves: %s", len(legal_moves), str(legal_moves))

        # Check for some legal moves - if none return score of this board
        if len(legal_moves) == 0:
            return self.score(game, self),(-1,-1)

        # Perform max layer search       
        if maximizing_player:
            value = -inf
            best_move_so_far = (-1,-1)
            for m in legal_moves:
                logging.debug("  Max layer - trying this move: %s", str(m))
                #value = max(value,self.alphabeta(game.forecast_move(m), depth-1, alpha, beta, not maximizing_player)[0])
                this_value, _ = self.alphabeta(game.forecast_move(m), depth-1, alpha, beta, not maximizing_player)
                if this_value > value:
                    value = this_value
                    best_move_so_far = m
                if value >= beta:
                    #logging.debug("  Returning %f, %s", value, str(best_move_so_far))
                    return value,m
                alpha = max(alpha, value)
            #logging.debug("  Returning %f, %s", value, str(best_move_so_far))
            return value, best_move_so_far
            
        # Perform min layer search       
        else:
            value = inf
            best_move_so_far = (-1,-1)
            for m in legal_moves:
                #logging.debug("  Min layer - trying this move: %s", str(m))
                this_value, _ = self.alphabeta(game.forecast_move(m), depth-1, alpha, beta, not maximizing_player)
                if this_value < value:
                    value = this_value
                    best_move_so_far = m
                if value <= alpha:
                    #logging.debug("  Returning %f, %s", value, str(best_move_so_far))
                    return value,m
                beta = min(beta, value)
            #logging.debug("  Returning %f, %s", value, str(best_move_so_far))
            return value, m



        
        
        