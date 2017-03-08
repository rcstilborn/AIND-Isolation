'''
this is a multi-process version of tournament.py to take advantage of multi-core machines
 Created on Mar 7, 2017

@author: richard
'''
from multiprocessing import Process, Pool, TimeoutError
from collections import namedtuple
import itertools

from tournament import play_match
from isolation import Board
from sample_players import RandomPlayer, null_score, open_move_score, improved_score
from game_agent import CustomPlayer, custom_score
from parameterized_evaluation_function import EvaluationFunction

NUM_MATCHES = 5  # number of matches against each opponent
TIME_LIMIT = 150  # number of milliseconds before timeout

TIMEOUT_WARNING = "One or more agents lost a match this round due to " + \
                  "timeout. The get_move() function must return before " + \
                  "time_left() reaches 0 ms. You will need to leave some " + \
                  "time for the function to return, and may need to " + \
                  "increase this margin to avoid timeouts during  " + \
                  "tournament play."

Agent = namedtuple("Agent", ["player", "name"])

def play_round(agents, opponent, num_matches):
    """
    Play one round (i.e., a single match between each pair of opponents)
    """
    wins = 0.
    total = 0.

    print("Playing matches against: ", opponent.name)
    #print("----------")

    for idx, agent_2 in enumerate(agents[:-1]):

        counts = {opponent.player: 0., agent_2.player: 0.}
        names = [opponent.name, agent_2.name]
        #print("  Match {}: {!s:^11} vs {!s:^11}".format(idx + 1, *names), end=' ')

        # Each player takes a turn going first
        for p1, p2 in itertools.permutations((opponent.player, agent_2.player)):
            for _ in range(num_matches):
                score_1, score_2 = play_match(p1, p2)
                counts[p1] += score_1
                counts[p2] += score_2
                total += score_1 + score_2

        wins += counts[opponent.player]

        #print("\tResult: {} to {}".format(int(counts[agent_1.player]),
        #                                  int(counts[agent_2.player])))
    #print("Returning score for ", opponent.name)

    return (opponent.name, (100. * wins / total))


def main():

    HEURISTICS = [("Null", null_score),
                  ("Open", open_move_score),
                  ("Improved", improved_score)]
    AB_ARGS = {"search_depth": 5, "method": 'alphabeta', "iterative": False}
    MM_ARGS = {"search_depth": 3, "method": 'minimax', "iterative": False}
    CUSTOM_ARGS = {"method": 'alphabeta', 'iterative': True}

    # Create a collection of CPU agents using fixed-depth minimax or alpha beta
    # search, or random selection.  The agent names encode the search method
    # (MM=minimax, AB=alpha-beta) and the heuristic function (Null=null_score,
    # Open=open_move_score, Improved=improved_score). For example, MM_Open is
    # an agent using minimax search with the open moves heuristic.
    mm_opponents = [Agent(CustomPlayer(score_fn=h, **MM_ARGS),
                       "MM_" + name) for name, h in HEURISTICS]
    ab_opponents = [Agent(CustomPlayer(score_fn=h, **AB_ARGS),
                       "AB_" + name) for name, h in HEURISTICS]
    random_opponents = [Agent(RandomPlayer(), "Random")]
    all_opponents = random_opponents + mm_opponents + ab_opponents
    
    test_agents = []
    # ID_Improved agent is used for comparison to the performance of the
    # submitted agent for calibration on the performance across different
    # systems; i.e., the performance of the student agent is considered
    # relative to the performance of the ID_Improved agent to account for
    # faster or slower computers.
    test_agents.append(Agent(CustomPlayer(score_fn=improved_score, **CUSTOM_ARGS), "ID_Improved"))
    
    # Create all the parameterized evaluation function objects
    # Then create all the test agents using those eval functions
    #params = zip(range(3), range(3), range(-2,2), range(3), range(3), range(-2,2))
    params = [(a,b,c,d,e,f) for a in range(1,3) 
                            for b in range(1,3) 
                            for c in range(-1,1) 
                            for d in range(1,3) 
                            for e in range(1,3) 
                            for f in range(-1,1)]

    for param in params:
        eval_obj = EvaluationFunction(param)
        test_agents.append(Agent(CustomPlayer(score_fn=eval_obj.eval_func, **CUSTOM_ARGS), "Student " + str(param)))
    print(len(test_agents))

    #print(DESCRIPTION)

    with Pool(processes=4) as pool:
        results = []
        for agentUT in test_agents:
            results.append(pool.apply_async(play_round, args=(all_opponents, agentUT, NUM_MATCHES)))

        for result in results:
            print(result.get())



if __name__ == '__main__':
    main()
