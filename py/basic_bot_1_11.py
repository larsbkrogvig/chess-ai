
# coding: utf-8

# In[ ]:

import sys
import chess
from time import sleep
from random import random, choice
from collections import defaultdict 

debug = True

def name():
	return "basic-1.11"


# # Parameters

# In[70]:

r = 0.05

value_piece = {
	chess.PAWN:   1.0,
	chess.KNIGHT: 2.95,
	chess.BISHOP: 3.05,
	chess.ROOK:   5.0,
	chess.QUEEN:  9.0,
	chess.KING:   0.0
}

# Position weight
wp = [[1,1,1,1,1,1,1,1],
	  [1,2,2,2,2,2,2,1],
	  [1,2,3,3,3,3,2,1],
	  [1,2,3,5,5,3,2,1],
	  [1,2,3,5,5,3,2,1],
	  [1,2,3,3,3,3,2,1],
	  [1,2,2,2,2,2,2,1],
	  [1,1,1,1,1,1,1,1]]
WP = sum(map(sum, wp))

# Attack weight (for black)
wa0 = [[3,4,4,4,4,4,4,3],
	   [3,4,4,4,4,4,4,3],
	   [2,3,3,3,3,3,3,2],
	   [2,3,3,3,3,3,3,2],
	   [1,2,2,2,2,2,2,1],
	   [1,2,2,2,2,2,2,1],
	   [1,1,1,1,1,1,1,1],
	   [1,1,1,1,1,1,1,1]]
WA = sum(map(sum, wa0))
wa = {}
wa[chess.WHITE] = wa0[::-1]
wa[chess.BLACK] = wa0


square_weight = {'pos': {},
				 'atk': {chess.WHITE: {},
						 chess.BLACK: {}}
				 }
for i in xrange(8):
	for j in xrange(8):
		square_weight['pos'][chess.square(j,i)] = wp[i][j]/float(WP)
		square_weight['atk'][chess.WHITE][chess.square(j,i)] = wa[chess.WHITE][i][j]/float(WA)
		square_weight['atk'][chess.BLACK][chess.square(j,i)] = wa[chess.BLACK][i][j]/float(WA)

def eval_board(board):

	if board.is_game_over():
		if board.is_checkmate():
			return -1 * (int(root_board.turn)-int(not root_board.turn)) * float('inf')
		else:
			return 0

	score = {chess.WHITE: {'material': 0, 'position': 0, 'attack': 0},
			 chess.BLACK: {'material': 0, 'position': 0, 'attack': 0}}
	for s in chess.SQUARES:
		p = board.piece_at(s)
		if p:
			score[p.color]['material'] += value_piece[p.piece_type]
			score[p.color]['position'] += square_weight['pos'][s]
		if board.is_attacked_by(chess.WHITE, s):
			score[chess.WHITE]['attack'] += square_weight['atk'][chess.WHITE][s]
		if board.is_attacked_by(chess.BLACK, s):
			score[chess.BLACK]['attack'] += square_weight['atk'][chess.BLACK][s]

	score_WHITE = score[chess.WHITE]['material'] + \
				  (1-r) * score[chess.WHITE]['position'] + \
				  r * score[chess.WHITE]['attack']
	score_BLACK = score[chess.BLACK]['material'] + \
				  (1-r) * score[chess.BLACK]['position'] + \
				  r * score[chess.BLACK]['attack']

	return score_WHITE - score_BLACK

def move(board, show=False):
	tree = build_tree(board)
	result = parse_tree(tree)
	#if debug:
	#  for r in result:
	#    print r
	return result[0].pop(0)

def build_tree(root_board, halfmove_depth=1, limit_halfmove_depth=2):

	if halfmove_depth == limit_halfmove_depth:
		leaf = []
		for move in root_board.legal_moves:
			root_board.push(move)
			fen = root_board.fen()
			root_board.pop()
			leaf.append((move, fen))
		return {root_board.fen(): leaf}
	else:
		branch = []
		for move in root_board.legal_moves:
			root_board.push(move)
			subbranch = build_tree(root_board, 
								   halfmove_depth=halfmove_depth+1,
								   limit_halfmove_depth=limit_halfmove_depth)
			root_board.pop()
			branch.append((move,subbranch))
		return {root_board.fen(): branch}
	pass

def parse_tree(tree):

	ans = _parse_tree(tree)
	return (ans[1:][::-1],ans[0])

def _parse_tree(tree, depth=0):

	root_board = chess.Board(tree.keys()[0])
	sign = int(root_board.turn) - int(not root_board.turn)

	movelist = tree.values()[0]

	# Is the game over?
	if root_board.is_game_over():
		if root_board.is_checkmate():
			ans = list((-1*float('inf'), None))
		else:
			ans = list((0, None))

	# Are there legal moves?
	elif movelist:

		if type(movelist[0][1])==str:
			sys.stdout.flush()

			leaf = []
			for (move,fen) in movelist:
				root_board.push(move)
				evl = eval_board(root_board)
				root_board.pop()
				leaf.append((sign*evl,move))
			ans = list(max(leaf))

		else:
			ansl = [(-1*t[0],t[1:]) for t in [_parse_tree(subtree,depth=depth+1)+[move] for (move, subtree) in movelist]]
			ans = max(ansl)
			ans = [ans[0]]+ans[1]

	else:
		raise Exception('The game is not over, but there are no legal moves!')

	return ans

