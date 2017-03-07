'''
Created on Mar 7, 2017

@author: richard
'''
import random

from isolation import Board
from sample_players import HumanPlayer
from sample_players import improved_score
from game_agent import CustomPlayer


if __name__ == '__main__':
    human = HumanPlayer()
    computer = CustomPlayer(score_fn=improved_score,method='alphabeta')
    # Randomize who goes first
    if (random.randint(0,1)):
        print("You are player 'O'")
        game = Board(human, computer)
    else:
        print("You are player 'X'")
        game = Board(computer, human)
    
    # Randominze first moves for each player
    for _ in range(2):
        game.apply_move(random.choice(game.get_legal_moves()))

    # Start playing!
    winner, _, reason = game.play()
    
    if winner == human:
        print("You won!!!", reason)
    else:
        print("You lost!!!", reason)