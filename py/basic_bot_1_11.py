
# coding: utf-8

# In[ ]:

import sys
import chess
from time import sleep
from random import random, choice
from collections import defaultdict 

debug = False

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

    # Check for draw
    if (board.is_stalemate() 
        or board.is_insufficient_material() 
        or board.is_seventyfive_moves()
        or board.is_fivefold_repetition()
        or board.can_claim_draw()
        ):
        return 0
    else:
        return eval_player(board, chess.WHITE) - eval_player(board, chess.BLACK)


def eval_player(board, player):
    
    score_material = 0
    score_presence = 0
    score_attacks = 0
    
    piece_squares = chess.SquareSet()
    attack_squares = chess.SquareSet()
    for piece_type in xrange(1,7):
        piece_type_squares = board.pieces(piece_type, player)
        piece_squares = piece_squares.union(piece_type_squares)
        for square in piece_type_squares:
            
            score_material += value_piece[piece_type]
            score_presence += square_weight['pos'][square]
            attack_squares = attack_squares.union(board.attacks(square))
    
    attack_squares = attack_squares.difference(piece_squares)

    score_attacks = reduce(lambda x,y: x+square_weight['atk'][player][y], attack_squares, 0)

    return score_material + (1-r)*score_presence + r*score_attacks


def move(board, show=False):
    tree = build_tree(board)
    result = parse_tree(tree)
    if debug:
      for r in result:
        print r
    return result[0].pop(0)


def board_push(board, move):
    new_board = board.copy()
    new_board.push(move)
    return new_board


def build_tree(root_board, halfmove_depth=1, limit_halfmove_depth=2):

    if halfmove_depth == limit_halfmove_depth:
        return {root_board.fen(): [(move, board_push(root_board, move).fen()) for move in root_board.legal_moves]}
    else:
        return {root_board.fen(): [(move, build_tree(board_push(root_board, move),
                                                     halfmove_depth=halfmove_depth+1,
                                                     limit_halfmove_depth=limit_halfmove_depth)) for move in root_board.legal_moves]}
    pass


def parse_tree(tree):

    ans = _parse_tree(tree)
    return (ans[1:][::-1],ans[0])


def _parse_tree(tree, depth=0):

    root_board = chess.Board(tree.keys()[0])
    sign = int(root_board.turn) - int(not root_board.turn)

    movelist = tree.values()[0]

    if movelist:

        if type(movelist[0][1])==str:
            sys.stdout.flush()
            ans = list(max([(sign*eval_board(board_push(root_board, move)),move) for (move,fen) in movelist]))
        else:
            ansl = [(-1*t[0],t[1:]) for t in [_parse_tree(subtree,depth=depth+1)+[move] for (move, subtree) in movelist]]
            ans = max(ansl)
            ans = [ans[0]]+ans[1]

    else:

        if board.is_checkmate():
            print "Looks like a checkmate"
            ans = list((float('inf'), None))
        else:
            print "This must be draw"
            ans = list((0, None))

    if debug and depth==0:
        for a in sorted(ansl):
            print a

    return ans


    

