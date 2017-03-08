'''
this is a multi-process version of tournament.py to take advantage of multi-core machines
 Created on Mar 7, 2017

@author: richard
'''
from multiprocessing import Pool
from collections import namedtuple
import sys, getopt, os, logging, itertools, datetime

from tournament import play_match
from isolation import Board
from sample_players import RandomPlayer, null_score, open_move_score, improved_score
from game_agent import CustomPlayer, ParameterizedEvaluationFunction

logging.basicConfig(level=logging.ERROR)

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

    #return opponent.name, 33.123456
    for idx, agent_2 in enumerate(agents[:-1]):

        counts = {opponent.player: 0., agent_2.player: 0.}
        names = [opponent.name, agent_2.name]

        # Each player takes a turn going first
        for p1, p2 in itertools.permutations((opponent.player, agent_2.player)):
            for _ in range(num_matches):
                score_1, score_2 = play_match(p1, p2)
                counts[p1] += score_1
                counts[p2] += score_2
                total += score_1 + score_2

        wins += counts[opponent.player]

    return opponent.name, (100. * wins / total)


def main(argv):

    USAGE = """usage: tournament_mp.py [-m <number of matches>] [-p <pool size>] [-o <outputfile>]
            -m number of matches: optional number of matches (each match has 4 games) - default is 5
            -p pool size: optional pool size - default is 3
            -o output file: optional output file name - default is results.txt"""
    
    # Assumes 2 x dual-core CPUs able to run 3 processes relatively
    # uninterrupted (interruptions cause get_move to timeout)
    pool_size = 3 
    outputfilename = 'results.txt'
    num_matches = NUM_MATCHES
    try:
        opts, args = getopt.getopt(argv,"hm:p:o:",["matches=", "poolsize=","ofile="])
    except getopt.GetoptError as err:
        print(err)
        print(USAGE)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(USAGE)
            sys.exit()
        elif opt in ("-m", "--matches"):
            num_matches = int(arg)
        elif opt in ("-p", "--poolsize"):
            pool_size = int(arg)
        elif opt in ("-o", "--ofile"):
            outputfilename = arg

    
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
    params = [(a,b,c,d,e,f) for a in range(1,3) 
                            for b in range(1,3) 
                            for c in range(-1,1) 
                            for d in range(1,3) 
                            for e in range(1,3) 
                            for f in range(-1,1)]
    #params = [(0,0,0,0,0,0)]
    for param in params:
        eval_obj = ParameterizedEvaluationFunction(param)
        test_agents.append(Agent(CustomPlayer(score_fn=eval_obj.eval_func, **CUSTOM_ARGS), "Student " + str(param)))
    
    # Put the start time in the output file
    with open(outputfilename, mode='a') as ofile:
        ofile.write('*******************************************************************************************\n')
        ofile.write('Starting Isolation tournament with %d test agents, %d games per round, and %d sub-processes\n' % 
               (len(test_agents), num_matches*4, pool_size))
        ofile.write('Tournament started at %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # Run the tournament!
    with Pool(processes=pool_size) as pool:
        results = []
        for agentUT in test_agents:
            results.append(pool.apply_async(play_round, args=(all_opponents, agentUT, num_matches)))

        # Write the output... flush each time as it takes a long time to run
        with open(outputfilename, mode='a') as ofile:
            for result in results:
                agent, res = result.get()
                ofile.write('%s got %2.2f\n' % (agent, res))
                ofile.flush()
            ofile.write('Tournament complete at: %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            ofile.write('*******************************************************************************************\n\n')


if __name__ == '__main__':
    main(sys.argv[1:])
