
# coding: utf-8

# In[ ]:

import sys
import chess
from time import sleep
from random import random, choice
from collections import defaultdict 

def name():
    return "basic-1.11b"


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
            return -1 * (int(board.turn)-int(not board.turn)) * float('inf')
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
    root = build_tree(board)
    result = parse_tree(root, debug=show)
    return result['line'].pop()

def build_tree(root_board, halfmove_depth=0, halfmove_depth_limit=2):

    # Make a leaf node if the game is over or we have reached the depth limit
    if root_board.is_game_over() or halfmove_depth == halfmove_depth_limit:
        return {'fen': root_board.fen(),
                'moves': []
                }

    # Make a branch
    else:
        new_root = {'fen': root_board.fen(),
                    'moves': list(root_board.legal_moves)
                    }

        for move in new_root['moves']:

            # Make a legal move
            root_board.push(move)

            # Add the resulting state ("depth first")
            new_root[move] = build_tree(root_board, 
                                        halfmove_depth=halfmove_depth+1,
                                        halfmove_depth_limit=halfmove_depth_limit)
            # Undo the move
            root_board.pop()

        return new_root


def parse_tree(root, depth=0, debug=False):

    # Get the direction to maximize the evaluation
    root_board = chess.Board(root['fen'])
    sign = int(root_board.turn) - int(not root_board.turn)

    # If this is a leaf node the game is over or the depth is reached
    if not root['moves']:

        return {'eval': eval_board(root_board),
                'line': []
                }

    # Return the best of the subnodes
    else:

        best_eval = -1*float('inf')

        # Check all possible next states
        nodes = []

        for move in root['moves']:
            node = parse_tree(root[move], depth=depth+1)

            nodes.append(node)

            # If the state is better, take it
            if sign*node['eval'] >= best_eval:
                best_eval = sign*node['eval']
                best_move = move
                best_node = node

        if debug and depth == 0:
            nodes = sorted(nodes, key=lambda k: k['eval'])
            print '\n'
            for node in nodes:
                print node
            print 'best:', best_node

        # Add the best move to the line, keep the evaluation
        best_node['line'].append(best_move)

        return best_node
