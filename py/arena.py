
# coding: utf-8

# In[ ]:

import sys
import os
import chess
from time import sleep, time
from datetime import datetime
from random import random, choice

datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')

# # Bots

# In[ ]:

import random_bot
import final_bot
import basic_bot


# ### Parameters

# In[ ]:

turn_color = {
	True:'WHITE',
	False:'BLACK',
	None: None
}


# ### Utility functions

# In[ ]:

def update_count(board, me):
	fmap = {
	    ( 'WIN', 'WHITE'):  'W_win',
	    ('DRAW', 'WHITE'): 'W_draw',
	    ('LOSE', 'WHITE'): 'W_lose',
	    ( 'WIN', 'BLACK'):  'B_win',
	    ('DRAW', 'BLACK'): 'B_draw',
	    ('LOSE', 'BLACK'): 'B_lose'}

	result = None
	if board.is_checkmate():
		if not board.turn == me:
			result = 'WIN'
		else:
			result = 'LOSE'
	else:
		result = 'DRAW'

	increment_counter(fmap[(result,turn_color[me])])

	pass

def increment_counter(fname):
	if os.path.exists('../html/'+fname):
		with open('../html/'+fname, 'r') as f:
			n = f.read()
		with open('../html/'+fname, 'w') as f:
			f.write(str(int(n)+1))
	else:
		with open('../html/'+fname, 'w') as f:
			f.write(str(1))
	pass

def get_status(board):
	result = ""
	if board.is_game_over():
		if board.is_checkmate(): result = 'Checkmate! ' + turn_color[not board.turn] + ' wins'
		if board.is_stalemate(): result = 'Stalemate! DRAW'
		if board.is_insufficient_material(): result = 'Insufficient material. DRAW', 
		if board.is_seventyfive_moves(): result = 'Seventyfive moves without capture or pawn move. DRAW'
		if board.is_fivefold_repetition(): result = 'Fivefold repetition. DRAW'
	else:
		result = turn_color[board.turn], 'to move'
	return result


# # The Arena

# In[ ]:

me_bot = basic_bot
he_bot = random_bot
players = [chess.WHITE, chess.BLACK]
min_turn_time = 1


# In[ ]:

while True:

	with open('../html/since', 'w') as f:
		f.write(datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S'))
	
	board = chess.Board() # Set up the board
	me = choice(players)  # My color

	with open('../html/player', 'w') as f:
		f.write('Bot plays '+turn_color[me]+', '+turn_color[not me]+' is random\n')
		
	turn=0
	while not board.is_game_over():
		
		t0 = time()
		turn+=1

		
		with open('../html/fen', 'w') as f:
			f.write(board.fen())
		
		if board.turn == me:
			with open('../html/status', 'w') as f:
				f.write(str(1+turn/2) + ' - My move, ' + turn_color[board.turn])
			move = me_bot.move(board) # My move!
		else:
			with open('../html/status', 'w') as f:
				f.write(str(1+turn/2) + ' - His move, ' + turn_color[board.turn])
			move = he_bot.move(board) # My opponent's move

		board.push(move) # Make the move

		t1 = time()
		if t1-t0 < min_turn_time:
			sleep(min_turn_time - (t1-t0))
			
	with open('../html/fen', 'w') as f:
			f.write(board.fen())
	
	with open('../html/status', 'w') as f:
		f.write(get_status(board))

	update_count(board, me)
		
	sleep(8)

