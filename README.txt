Implementation of an AI capable of playing the card game Briskola using Monte Carlo Tree Search.

####################################
HOW TO RUN:
python montecarlo.py

By pressing 'ENTER' you can move through the plays. The bottom player is the AI using MCTS.
The top player uses random moves. When it's MCTSs turn after pressing 'ENTER' it takes a
second to make the play.

After MCTS does a play you can scroll up to check the results it returned in the following form:

[card 1] [card 2] [card 3]
number of visits for each card
total reward collected for each card
normalised rewards (reward/visits) for each card

####################################
Command:
python 100x.py

runs 100 games and returns the achieved result.