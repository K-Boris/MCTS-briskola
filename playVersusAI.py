from __future__ import print_function
from timeit import default_timer as timer
import math
import random
import numpy as np
import time

SCALAR = 1/math.sqrt(2.0)

def newDeck():
	COLOR = [1,2,3,4]
	# 19 = trojka
	# 29 = as
	VALUE = [2,4,5,6,7,11,12,13,19,29]
	deck = []
	for i in range(0,4):
		for j in range(0,10):
			deck.append([COLOR[i],VALUE[j]])
	return deck

class Node():
	def __init__(self, state, parent=None):
		self.visits=0
		self.reward=0.0	
		self.state=state
		self.children=[]
		self.parent=parent	
	def add_child(self,child_state):
		child=Node(child_state,self)
		self.children.append(child)
	def update(self,reward):
		self.reward+=reward
		self.visits+=1
	def fully_expanded(self):
		if len(self.children)==len(self.state[0]):
			return True
		return False
	def terminal(self):
		if len(self.state[0])==0:
			return True
		return False
	def __repr__(self):
		s="Node; children: %d; visits: %d; reward: %f"%(len(self.children),self.visits,self.reward)
		return s

def selectBestChild(node,scalar):
	maxScore = 0.0
	bestChildren = []
	for c in node.children:
		score = 0
		if c.visits == 0:
			score = float('inf')
		else:
			exploit = c.reward/c.visits
			explore = math.sqrt(2*math.log(node.visits)/float(c.visits))
			score = exploit+scalar*explore
		if score == maxScore:
			bestChildren.append(c)
		if score > maxScore:
			bestChildren = [c]
			maxScore = score
	if len(bestChildren)==0:
		raise Exception('len(bestChildren)==0')
	return random.choice(bestChildren)

def backpropagation(node,reward):
	while node != None:
		node.visits+=1
		node.reward+=reward
		node = node.parent
	return

def validNode(node):
	myHand = list(node[0])
	table = list(node[1])
	deck = list(node[2])
	turn = node[5]
	oppHand = list(node[7])

	if len(table)==0:
		if len(myHand)>(len(oppHand)+len(deck)):
			return False
		if len(oppHand)>(len(myHand)+len(deck)):
			return False
	else:
		if turn==True:
			if len(myHand)-1>(len(oppHand)+len(deck)):
				return False
			if len(oppHand)>(len(myHand)-1+len(deck)):
				return False
		else:
			if len(myHand)+1>(len(oppHand)+len(deck)):
				return False
			if len(oppHand)>(len(myHand)+1+len(deck)):
				return False
	return True

# state:
	# 0 my hand
	# 1 table
	# 2 deck
	# 3 briskula
	# 4 points
	# 5 whose turn
	# 6 dropping this turn
	# 7 opponent hand
def monteCarlo(budget,node):
	if len(node.state[1])>0:
		node.state[1]=list(node.state[1][0])
	# preveri ce je igra v fazi, ko so vse karte znane
	if len(node.state[2])!=0:	# v decku so se vedno karte, ne vemo kaj ima nasprotnik
		node.state[2] = list(node.state[2])+list(node.state[7])
		node.state[7] = []

	currState=node.state[0]
	for card in currState:
		tempHand = list(currState)
		tempHand.remove(card)
		if len(node.state[1])==0:	# ce na mizi ni kart, je v naslednjem koraku na vrsti nasprotnik
			if validNode(list([list(tempHand),list(card),list(node.state[2]),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(node.state[7])])):
				node.add_child([list(tempHand),list(card),list(node.state[2]),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(node.state[7])])
		else:						# ce na mizi ze je karta, je v naslednjem koraku na vrsti tisti, ki zmaga
			whosTurn = whoWins(list(node.state[1]),list(card),list(node.state[3]),node.state[5])
			points = list(node.state[4])
			if whosTurn==True:				
				points[0] += collectPoints(list(node.state[1]),list(card))
			else:
				points[1] += collectPoints(list(node.state[1]),list(card))
			oppHand = list(node.state[7])
			if (len(tempHand)+len(node.state[2])+len(oppHand))==5:	# vemo kdo dobi briskolo
				if whosTurn==True:
					oppHand = oppHand+[list(node.state[3])]
				else:
					tempHand = list(tempHand)+[list(node.state[3])]
			if validNode(list([list(tempHand),[],list(node.state[2]),list(node.state[3]),list(points),whosTurn,list(card),list(oppHand)])):
				node.add_child([list(tempHand),[],list(node.state[2]),list(node.state[3]),list(points),whosTurn,list(card),list(oppHand)])
	start = timer()
	end = timer()
	#for iter in range(budget):
	while end-start<budget:
		####### SELECTION - phase 1 #######
		while len(node.children)>0:
			node = selectBestChild(node,SCALAR)

		####### EXPANSION - phase 2 #######
		# An unvisited child position is randomly chosen and new record node is added to the tree of statistics
		if node.visits>0:
			if node.state[5]==True:		# na vrsti sem jaz, moram upostevat se karte, ki jih imam v roki
				if len(node.state[1])==0:					# ce na mizi ni kart, je v naslednjem koraku na vrsti druga oseba
					for card in node.state[0]:					# za vsako karto v roki
						tempHand = list(node.state[0])
						tempHand.remove(card)
						if validNode(list([list(tempHand),list(card),list(node.state[2]),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(node.state[7])])):
							node.add_child([list(tempHand),list(card),list(node.state[2]),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(node.state[7])])					
					
				else:										# ce na mizi ze je karta, je v naslednjem koraku na vrsti tisti, ki zmaga
					for card in node.state[0]:					# za vsako karto v roki
						whosTurn = whoWins(node.state[1],card,node.state[3],node.state[5])
						points = list(node.state[4])
						if whosTurn==True:				
							points[0] += collectPoints(node.state[1],card)
						else:
							points[1] += collectPoints(node.state[1],card)
						tempHand = list(node.state[0])
						tempHand.remove(card)
						oppHand = list(node.state[7])
						if (len(tempHand)+len(node.state[2])+len(oppHand))==5:	# vemo kdo dobi briskolo
							if whosTurn==True:
								oppHand = oppHand+[list(node.state[3])]
							else:
								tempHand = tempHand+[list(node.state[3])]
						if validNode(list([list(tempHand),[],list(node.state[2]),list(node.state[3]),list(points),whosTurn,list(card),list(oppHand)])):
							node.add_child([list(tempHand),[],list(node.state[2]),list(node.state[3]),list(points),whosTurn,list(card),list(oppHand)])

			else:						# na vrsti je nasprotnik, moram upostevat se karte, ki jih ima v roki; ce vemo kaj sploh ima, npr briskula, ali pa v zadnjih krogih, ko vemo katere karte ima
				if len(node.state[1])==0:					# ce na mizi ni kart, je v naslednjem koraku na vrsti druga oseba
					for card in node.state[7]:					# za vsako karto v roki
						tempHand = list(node.state[7])
						tempHand.remove(card)
						if validNode(list([list(node.state[0]),list(card),list(node.state[2]),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(tempHand)])):
							node.add_child([list(node.state[0]),list(card),list(node.state[2]),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(tempHand)])
					
				else:										# ce na mizi ze je karta, je v naslednjem koraku na vrsti tisti, ki zmaga
					for card in node.state[7]:					# za vsako karto v roki
						whosTurn = whoWins(node.state[1],card,node.state[3],node.state[5])
						points = list(node.state[4])
						if whosTurn==True:				
							points[0] += collectPoints(node.state[1],card)
						else:
							points[1] += collectPoints(node.state[1],card)
						tempHand = list(node.state[7])
						tempHand.remove(card)
						myHand = list(node.state[0])
						if (len(node.state[0])+len(node.state[2])+len(tempHand))==5:	# vemo kdo dobi briskolo
							print("This should probably never happen, if it does, re-check.") # briskula je ze porazdeljena, ker ce ne, ne bi imel nasprotnik kart v roki
							if whosTurn==True:
								tempHand = tempHand+[list(node.state[3])]
							else:
								myHand = myHand+[list(node.state[3])]
						myHand = node.state[0]
						if validNode(list([list(myHand),[],list(node.state[2]),list(node.state[3]),list(points),whosTurn,list(card),list(tempHand)])):
							node.add_child([list(myHand),[],list(node.state[2]),list(node.state[3]),list(points),whosTurn,list(card),list(tempHand)])

			if len(node.state[1])==0:					# ce na mizi ni kart, je v naslednjem koraku na vrsti druga oseba
				for card in node.state[2]:					# za vsako karto v decku
					tempDeck = list(node.state[2])
					tempDeck.remove(card)
					if validNode(list([list(node.state[0]),list(card),list(tempDeck),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(node.state[7])])):
						node.add_child([list(node.state[0]),list(card),list(tempDeck),list(node.state[3]),list(node.state[4]),not node.state[5],list(card),list(node.state[7])])
			else:										# ce na mizi ze je karta, je v naslednjem koraku na vrsti tisti, ki zmaga
				for card in node.state[2]:					# za vsako karto v decku
						whosTurn = whoWins(node.state[1],card,node.state[3],node.state[5])
						points = list(node.state[4])
						if whosTurn==True:				
							points[0] += collectPoints(node.state[1],card)
						else:
							points[1] += collectPoints(node.state[1],card)
						tempDeck = list(node.state[2])
						tempDeck.remove(card)
						tempHand = list(node.state[0])
						oppHand = list(node.state[7])
						if (len(tempHand)+len(tempDeck)+len(oppHand))==5:	# vemo kdo dobi briskolo
							if whosTurn==True:
								oppHand = oppHand+[list(node.state[3])]
							else:
								tempHand = tempHand+[list(node.state[3])]
						if validNode(list([list(tempHand),[],list(tempDeck),list(node.state[3]),list(points),whosTurn,list(card),list(oppHand)])):
							node.add_child([list(tempHand),[],list(tempDeck),list(node.state[3]),list(points),whosTurn,list(card),list(oppHand)])
			node = selectBestChild(node,SCALAR)

		####### SIMULATION - phase 3 #######
		# Randomly play the game till the end
		if len(node.state[0])==0 and len(node.state[1])==0 and len(node.state[2])==0 and len(node.state[7])==0:
			####### return to node
			while node.parent!=None:
				node = node.parent
			# update time
			end = timer()
			continue
		reward = simulateGame(node.state)

		####### BACK-PROPAGATION - phase 4 #######
		# Update the tree
		backpropagation(node,reward)

		####### return to node
		while node.parent!=None:
			node = node.parent

		# update time
		end = timer()

	#return node
	return selectBestChild(node,0)

def treePolicy(node):
	while node.terminal()==False:
		if node.fully_expanded()==False:
			return expand(node)
		else:
			node=selectBestChild(node,SCALAR)
	return node

def expand(node):
	for currState in node.state[0]:
		node.add_child()

# state:
	# 0 my hand
	# 1 table
	# 2 deck
	# 3 briskula
	# 4 points
	# 5 whose turn
	# 6 dropping this turn
	# 7 opponent hand
def simulateGame(state):
	myHand = list(state[0])
	table = list(state[1])
	deck = list(state[2])
	briskula = list(state[3])
	points = list(state[4])
	turn = state[5]
	oppHand = list(state[7])
	#print('ENTER = ',len(myHand)+len(deck)+len(oppHand),' my hand ',myHand,' table ',table,' oppHand ', oppHand,' briskula ',briskula,' deck ',deck,' turn ',turn)
	if (len(myHand)+len(oppHand)+len(deck))==1:
		#print('ENTER = ',len(myHand)+len(deck)+len(oppHand),' my hand ',myHand,' table ',table,' oppHand ', oppHand,' briskula ',briskula,' deck ',deck,' turn ',turn)
		if turn==True:
			if len(myHand)>0:
				card = myHand.pop()
			else:
				card = deck.pop()
		else:
			if len(oppHand)>0:
				card = oppHand.pop() 
			else:
				card = deck.pop()
		whosTurn = whoWins(table,card,briskula,turn)
		if whosTurn==True:				
			points[0] += collectPoints(table,card)
		else:
			points[1] += collectPoints(table,card)
		table = []
		return points[0]

	if len(table)>0: 	# 1 card on table, still has to drop a card
		if turn==True:
			if len(myHand)-1<len(oppHand)+len(deck):
				if len(myHand)==3:
					card = myHand.pop(random.randint(0,len(myHand)-1))
				else:
					if len(myHand)>0 and len(deck)>0:
						if random.randint(0,1)==0:
							card = myHand.pop(random.randint(0,len(myHand)-1))
						else:
							card = deck.pop(random.randint(0,len(deck)-1))
					elif len(myHand)>0:
						card = myHand.pop(random.randint(0,len(myHand)-1))
					elif len(deck)>0:
						card = deck.pop(random.randint(0,len(deck)-1))
					else:
						raise Exception('No cards in hand or deck')
			else:
				card = myHand.pop(random.randint(0,len(myHand)-1))
			turn = whoWins(table,card,briskula,turn)
			if turn==True:				
				points[0] += collectPoints(table,card)
			else:
				points[1] += collectPoints(table,card)
			table = []
		else:
			if len(oppHand)==3:
				card = oppHand.pop(random.randint(0,len(oppHand)-1))
			else:
				if len(oppHand)>0 and len(deck)>0:
					if random.randint(0,1)==0:
						card = oppHand.pop(random.randint(0,len(oppHand)-1))
					else:
						card = deck.pop(random.randint(0,len(deck)-1))
				elif len(oppHand)>0:
					card = oppHand.pop(random.randint(0,len(oppHand)-1))
				elif len(deck)>0:
					card = deck.pop(random.randint(0,len(deck)-1))
				else:
					raise Exception('No cards in hand or deck')
			turn = whoWins(table,card,briskula,turn)
			if turn==True:				
				points[0] += collectPoints(table,card)
			else:
				points[1] += collectPoints(table,card)
			table = []

		if (len(myHand)+len(deck)+len(oppHand))==5:
			if turn==True:
				oppHand = oppHand+[briskula]
			else:
				myHand = myHand+[briskula]
			while len(myHand)<3:
				card = deck.pop(random.randint(0,len(deck)-1))
				myHand.append(card)
			while len(oppHand)<3:
				card = deck.pop(random.randint(0,len(deck)-1))
				oppHand.append(card)

	while (len(myHand)+len(deck)+len(oppHand))>5 and len(deck)>0:
		if turn==True:
			if len(myHand)<3:
				while len(myHand)!=3:
					card = deck.pop(random.randint(0,len(deck)-1))
					myHand.append(card)
			card = myHand.pop(random.randint(0,len(myHand)-1))
			table = card
			turn = not turn
			card = deck.pop(random.randint(0,len(deck)-1))

			turn = whoWins(table,card,briskula,turn)
			if turn==True:				
				points[0] += collectPoints(table,card)
			else:
				points[1] += collectPoints(table,card)
			table = []
		else:
			card = deck.pop(random.randint(0,len(deck)-1))
			table = card
			turn = not turn
			if len(myHand)<3:
				while len(myHand)!=3:
					card = deck.pop(random.randint(0,len(deck)-1))
					myHand.append(card)
			card = myHand.pop(random.randint(0,len(myHand)-1))
			turn = whoWins(table,card,briskula,turn)
			if turn==True:				
				points[0] += collectPoints(table,card)
			else:
				points[1] += collectPoints(table,card)
			table = []

		if (len(myHand)+len(deck)+len(oppHand))==5:
			if turn==True:
				oppHand = oppHand+[briskula]
			else:
				myHand = myHand+[briskula]
			while len(myHand)<3:
				card = deck.pop(random.randint(0,len(deck)-1))
				myHand.append(card)
			while len(oppHand)<3:
				card = deck.pop(random.randint(0,len(deck)-1))
				oppHand.append(card)

	#print('BEFORE ',myHand,' opp ',oppHand,' table ',table,' deck ',deck, ' briskula ',briskula,' turn ',turn)
	if (len(myHand)+len(oppHand)+len(deck))==6:
		while len(myHand)<3:
			card = deck.pop(random.randint(0,len(deck)-1))
			myHand.append(card)
		while len(oppHand)<3:
			card = deck.pop(random.randint(0,len(deck)-1))
			oppHand.append(card)
	if (len(myHand)+len(oppHand)+len(deck))==4:
		while len(myHand)<2:
			card = deck.pop(random.randint(0,len(deck)-1))
			myHand.append(card)
		while len(oppHand)<2:
			card = deck.pop(random.randint(0,len(deck)-1))
			oppHand.append(card)
	if (len(myHand)+len(oppHand)+len(deck))==2:
		while len(myHand)<1:
			card = deck.pop(random.randint(0,len(deck)-1))
			myHand.append(card)
		while len(oppHand)<1:
			card = deck.pop(random.randint(0,len(deck)-1))
			oppHand.append(card)

	#print('WHILE ',myHand,' opp ',oppHand,' table ',table,' deck ',deck, ' briskula ',briskula)
	while len(myHand)>0:
		if turn==True:
			card = myHand.pop(random.randint(0,len(myHand)-1))
			table = card
			turn = not turn
			card = oppHand.pop(random.randint(0,len(oppHand)-1))

			turn = whoWins(table,card,briskula,turn)
			if turn==True:				
				points[0] += collectPoints(table,card)
			else:
				points[1] += collectPoints(table,card)
			table = []
		else:
			card = oppHand.pop(random.randint(0,len(oppHand)-1))
			table = card
			turn = not turn
			card = myHand.pop(random.randint(0,len(myHand)-1))
			turn = whoWins(table,card,briskula,turn)
			if turn==True:				
				points[0] += collectPoints(table,card)
			else:
				points[1] += collectPoints(table,card)
			table = []

	return points[0]/60.0
	

# whoWins - return whose turn it is
# turn - True : my turn
#		 False : opponent turn
def whoWins(table,card,briskula,turn):
	if table[0] == briskula[0]:
		if card[0] != briskula[0]:
			return not turn
		else:
			if table[1]>card[1]:
				return not turn
			else:
				return turn
	elif card[0] == briskula[0]:
		return turn
	else:
		if table[0] != card[0]:
			return not turn
		else:
			if table[1]>card[1]:
				return not turn
			else:
				return turn

def valueOfCard(card):
	if card[1] < 10:
		return 0
	else:
		val = map(int,str(card[1]))
		return val[0]+val[1]

def collectPoints(card1,card2):
	return valueOfCard(card1)+valueOfCard(card2)

def nextPlayer(currentPlayer):
	if currentPlayer == 0:
		return 1
	else:
		return 0

def whoWinsReal(table,card,briskula,turn):
	if table[0] == briskula[0]:
		if card[0] != briskula[0]:
			return nextPlayer(turn)
		else:
			if table[1]>card[1]:
				return nextPlayer(turn)
			else:
				return turn
	elif card[0] == briskula[0]:
		return turn
	else:
		if table[0] != card[0]:
			return nextPlayer(turn)
		else:
			if table[1]>card[1]:
				return nextPlayer(turn)
			else:
				return turn

def drawBoardState(playerHand,table,playerPoints,deck,briskula,turn):
	print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
	print('Deck: ',len(deck),' cards         Briskula: ',briskula)
	# Draw top player hand
	if turn==1:
		print('Player B hand           Points: ',playerPoints[1],' <<<')
	else:
		print('Player B hand           Points: ',playerPoints[1])
	for card in playerHand[1]:
		print('####### ', end='')
	print()
	for card in playerHand[1]:
		print('#     # ',end='')
	print()
	for card in playerHand[1]:
		print('#  '+str(card[0])+'  # ',end='')
	print()
	for card in playerHand[1]:
		print('#  '+str(card[1])+'  # ',end='')
	print()
	for card in playerHand[1]:
		print('#     # ',end='')
	print()
	for card in playerHand[1]:
		print('####### ',end='')
	print()

	# Draw table
	print('\n\n')
	for card in table:
		print('####### ', end='')
	print()
	for card in table:
		print('#     # ',end='')
	print()
	for card in table:
		print('#  '+str(card[0])+'  # ',end='')
	print()
	for card in table:
		print('#  '+str(card[1])+'  # ',end='')
	print()
	for card in table:
		print('#     # ',end='')
	print()
	for card in table:
		print('####### ',end='')
	print('\n\n')

	# Draw bottom player hand
	for card in playerHand[0]:
		print('####### ',end='')
	print()
	for card in playerHand[0]:
		print('#     # ',end='')
	print()
	for card in playerHand[0]:
		print('#  ?  # ',end='')
	print()
	for card in playerHand[0]:
		print('#  ?  # ',end='')
	print()
	for card in playerHand[0]:
		print('#     # ',end='')
	print()
	for card in playerHand[0]:
		print('####### ',end='')
	print()
	if turn==0:
		print('Player A hand           Points: ',playerPoints[0],' <<<')
	else:
		print('Player A hand           Points: ',playerPoints[0])
	#raw_input("Press Enter to continue...")

def userInput(numOfCards):
	while True:
		try:
			inp = int(raw_input("YOUR TURN! Drop a card: "))
			if inp >= 1 and inp <= numOfCards:
				return inp-1
			else:
				continue
		except ValueError:
			print("Please input a number (1, 2 or 3, depending on which card you want to drop).")
			continue

###### MAIN ######
table = []
deck = []
playerHand = [[] for i in range(2)]
points = [0,0]
currentPlayer = 0

deck = newDeck()
np.random.shuffle(deck)

# ###########################
# START OF THE GAME
# ###########################
# Each player draws 3 cards
playerHand[0].append(deck.pop())
playerHand[0].append(deck.pop())
playerHand[0].append(deck.pop())
playerHand[1].append(deck.pop())
playerHand[1].append(deck.pop())
playerHand[1].append(deck.pop())

briskula = deck.pop()

currentPlayer = random.randint(0,1)

drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)

while len(deck)>1:
	# both players drop a card
	for h in range(0,2):
		if currentPlayer==0:
			node = Node([playerHand[0],table,deck,briskula,points,True,[],playerHand[1]])
			monte = monteCarlo(3,node)

			a = monte.parent
			print(a.children[0].state[6],' ',a.children[1].state[6],' ',a.children[2].state[6])
			print(a.children[0].visits,' ',a.children[1].visits,' ',a.children[2].visits)
			print(a.children[0].reward,' ',a.children[1].reward,' ',a.children[2].reward)
			print(a.children[0].reward/a.children[0].visits,' ',a.children[1].reward/a.children[1].visits,' ',a.children[2].reward/a.children[2].visits)
		
			table.append(playerHand[currentPlayer].pop(playerHand[currentPlayer].index(monte.state[6])))
		else:
			table.append(playerHand[currentPlayer].pop(userInput(3)))   #random.randint(0,2)))
		if h==0:
			currentPlayer = nextPlayer(currentPlayer)			
		drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)

	# evaluate who wins
	currentPlayer = whoWinsReal(table[0],table[1],briskula,currentPlayer)
	points[currentPlayer] += collectPoints(table[0],table[1])
	time.sleep(2)
	table.pop()
	table.pop()
	drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)

	# both players draw a card
	playerHand[currentPlayer].append(deck.pop())
	currentPlayer = nextPlayer(currentPlayer)
	time.sleep(2)
	drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
	playerHand[currentPlayer].append(deck.pop())
	currentPlayer = nextPlayer(currentPlayer)
	time.sleep(2)
	drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)

# 2 cards remain in deck,
# both players drop a card
if currentPlayer==0:
	node = Node([playerHand[0],table,deck,briskula,points,True,[],playerHand[1]])
	monte = monteCarlo(1,node)
	table.append(playerHand[currentPlayer].pop(playerHand[currentPlayer].index(monte.state[6])))
else:
	table.append(playerHand[currentPlayer].pop(userInput(3)))    #random.randint(0,2)))
currentPlayer = nextPlayer(currentPlayer)
drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
time.sleep(2)
if currentPlayer==0:
	node = Node([playerHand[0],table,deck,briskula,points,True,[],playerHand[1]])
	monte = monteCarlo(1,node)
	table.append(playerHand[currentPlayer].pop(playerHand[currentPlayer].index(monte.state[6])))
else:
	table.append(playerHand[currentPlayer].pop(userInput(3)))    #random.randint(0,2)))
drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
time.sleep(2)
# evaluate who wins
currentPlayer = whoWinsReal(table[0],table[1],briskula,currentPlayer)
points[currentPlayer] += collectPoints(table[0],table[1])
table.pop()
table.pop()
drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
time.sleep(2)

# draw last 2 cards
playerHand[currentPlayer].append(deck.pop())
currentPlayer = nextPlayer(currentPlayer)
drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
time.sleep(2)
playerHand[currentPlayer].append(briskula)
currentPlayer = nextPlayer(currentPlayer)
drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
time.sleep(2)

# play the hand to the end
for i in range(0,3):
	# both players drop a card
	for h in range(0,2):
		if currentPlayer==0:
			node = Node([playerHand[0],table,deck,briskula,points,True,[],playerHand[1]])
			monte = monteCarlo(1,node)
			table.append(playerHand[currentPlayer].pop(playerHand[currentPlayer].index(monte.state[6])))
		else:
			table.append(playerHand[currentPlayer].pop(userInput(len(playerHand[currentPlayer]))))    #random.randint(0,len(playerHand[currentPlayer])-1)))
		drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
		if h==0:
			currentPlayer = nextPlayer(currentPlayer)
	# evaluate who wins
	time.sleep(2)
	currentPlayer = whoWinsReal(table[0],table[1],briskula,currentPlayer)
	points[currentPlayer] += collectPoints(table[0],table[1])
	table.pop()
	table.pop()
	drawBoardState(playerHand,table,points,deck,briskula,currentPlayer)
	time.sleep(2)

# ###########################
# END OF THE GAME
# ###########################
print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
print("***End of the game.***")
if points[0]>points[1]:
	print("Player A won with "+str(points[0])+". CONGRATULATIONS!")
	print("Player B collected "+str(points[1])+" points.")
elif points[1]>points[0]:
	print("Player B won with "+str(points[1])+". CONGRATULATIONS!")
	print("Player A collected "+str(points[0])+" points.")
elif points[0]==points[1]:
	print("The game ended in a DRAW. Both players collected 60 points.")