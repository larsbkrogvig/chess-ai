
# coding: utf-8

# In[ ]:

import sys
import chess
from time import sleep
from random import random, choice
from collections import defaultdict 

def name():
    return "basic-1.0"


# # Parameters

# In[70]:

value_piece = {
    chess.PAWN:   1.0,
    chess.KNIGHT: 2.9,
    chess.BISHOP: 3.1,
    chess.ROOK:   5.0,
    chess.QUEEN:  9.0,
    chess.KING:   0.0
}

f = 1/6.
w = [[1,1,1,1,1,1,1,1],
     [1,2,2,2,2,2,2,1],
     [1,2,3,3,3,3,2,1],
     [1,2,3,5,5,3,2,1],
     [1,2,3,5,5,3,2,1],
     [1,2,3,3,3,3,2,1],
     [1,2,2,2,2,2,2,1],
     [1,1,1,1,1,1,1,1]]

square_importance = {}
for i,r in enumerate(w):
    for j,c in enumerate(r):
        square_importance[chess.square(i,j)] = f*((c-1)/(5.-1))

def eval_next_board(board, move):
    board_next = board.copy()
    board_next.push(move)
    return eval_board(board_next)

def eval_board(board):
    
    if board.is_game_over():
        if board.is_checkmate(): 
            result = -1 * (int(board.turn) - int(not board.turn)) * float('inf')
        else:
            result = 0
    else:
        result = eval_player(board, chess.WHITE) - eval_player(board, chess.BLACK)
        
    return result

def eval_player(board, player):
    
    score_material = 0
    score_presence = 0
    score_position = 0
    
    for piece_type in xrange(1,7):
        for square in board.pieces(piece_type, player):
            
            score_material += value_piece[piece_type]
            score_presence += square_importance[square]
        
        for square in board.pieces(piece_type, not player):
            
            attackers = sorted([value_piece[board.piece_type_at(s)] for s in board.attackers(board.turn, square)])
            defenders = sorted([value_piece[board.piece_type_at(s)] for s in board.attackers(not board.turn, square)])
            
            defendant = value_piece[piece_type]
            gain = 0
            while attackers:
                gain += defendant
                if defenders:
                    gain -= attackers.pop(0)
                    defendand = defenders.pop(0)
                else: 
                    break
                    
            score_position += max(0, (player==board.turn) * gain)

    return score_material + score_presence + score_position


def best_moves(board, cap = 4):
    
    legal_moves = board.legal_moves
    
    rated_moves = sorted([
            (eval_next_board(board, move), move) for move in legal_moves
            ], reverse = board.turn)

    return [move for i, (score, move) in enumerate(rated_moves) if i < cap]


def move(board, show=False):
               
    return best_moves(board).pop(0)
    

