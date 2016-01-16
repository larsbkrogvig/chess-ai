import sys
import chess
from time import sleep
from random import random, choice
from collections import defaultdict

class ChessMeta(object):

    def __init__(self, player):
        """Return a new ChessMeta object"""
        self.player = player
        self.material = 0


class ChessBot(object):

    def __init__(self, r=0.05):
        """Return a new ChessBot object"""
        self.name = 'basic-1.2'
        self.board = chess.Board()
        self.meta = {
            chess.WHITE: ChessMeta(chess.WHITE),
            chess.BLACK: ChessMeta(chess.BLACK)
            }
        self.square_weight = None
        self.value_piece = None
        self.tree = None
        self.r = r

        self._init_weight()

    def move(self, inboard, debug=False):
        """Return the best move on the given chess.Board 'inboard'."""

        # Update own board with opponent's move
        if inboard.move_stack:
            move_opponent = inboard.peek()
            self.board.push(move_opponent)

        # Build a move tree
        self.tree = self._build_tree()

        # Evaluate the move tree
        result = self._parse_tree(self.tree, debug=debug)

        # Get the first move in the best line (last move in revered list)
        move_self = result['line'].pop()

        # Update own board with own move
        self.board.push(move_self)

        # Return the chosen move to the arena board
        return move_self

    def _build_tree(self, halfmove_depth=0, halfmove_depth_limit=2):
        """Return a tree of positions to evaluate to find the best move"""

        # Make a leaf node if the game is over or we have reached the depth limit
        if self.board.is_game_over() or halfmove_depth == halfmove_depth_limit:
            return {'fen': self.board.fen(),
                    'moves': []
                    }
    
        # Make a branch
        else:
            new_root = {'fen': self.board.fen(),
                        'moves': list(self.board.legal_moves)
                        }
    
            if halfmove_depth == 0:
                new_root['board'] = self.board
    
            for move in new_root['moves']:
    
                # Make a legal move
                self.board.push(move)
    
                # Add the resulting state ("depth first")
                new_root[move] = self._build_tree(halfmove_depth=halfmove_depth+1,
                                                  halfmove_depth_limit=halfmove_depth_limit)
                                                  
                # Undo the move
                self.board.pop()
    
            return new_root

    def _parse_tree(self, tree_root, root_board=None, depth=0, debug=False):
    
        if depth == 0:
            root_board = tree_root['board']
    
        # Get the direction to maximize the evaluation
        sign = int(root_board.turn) - int(not root_board.turn)
    
        # If this is a leaf node the game is over or the depth is reached
        if not tree_root['moves']:
    
            return {'eval': self._eval_board(root_board),
                    'line': []
                    }
    
        # Return the best of the subnodes
        else:
    
            best_eval = -1*float('inf')
    
            # Check all possible next states
            for move in tree_root['moves']:
    
                # Make the move
                root_board.push(move)
    
                # Evaluate the new state
                node = self._parse_tree(tree_root[move], root_board=root_board, depth=depth+1)
    
                # Undo the move
                root_board.pop()
    
                # Show evaluation of all top level moves?
                if debug and depth == 0:
                    debug_node = node
                    debug_node['line'].append(move)
                    print debug_node
    
                # If the state is better, take it
                if sign*node['eval'] >= best_eval:
                    best_eval = sign*node['eval']
                    best_move = move
                    best_node = node
    
            # Add the best move to the line, keep the evaluation
            best_node['line'].append(best_move)
    
            return best_node

    def _eval_board(self, board):

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
                score[p.color]['material'] += self.value_piece[p.piece_type]
                score[p.color]['position'] += self.square_weight['pos'][s]
            if board.is_attacked_by(chess.WHITE, s):
                score[chess.WHITE]['attack'] += self.square_weight['atk'][chess.WHITE][s]
            if board.is_attacked_by(chess.BLACK, s):
                score[chess.BLACK]['attack'] += self.square_weight['atk'][chess.BLACK][s]
    
        score_WHITE = score[chess.WHITE]['material'] + \
                      (1-self.r) * score[chess.WHITE]['position'] + \
                      self.r * score[chess.WHITE]['attack']
        score_BLACK = score[chess.BLACK]['material'] + \
                      (1-self.r) * score[chess.BLACK]['position'] + \
                      self.r * score[chess.BLACK]['attack']
    
        return score_WHITE - score_BLACK

    def _init_weight(self):
        """Return a square value dictionary"""

        self.value_piece = {
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
        
        
        square_weight = {
            'pos': {},
            'atk': {
                chess.WHITE: {},
                chess.BLACK: {}
            }
        }

        for i in xrange(8):
            for j in xrange(8):
                square_weight['pos'][chess.square(j,i)] = wp[i][j]/float(WP)
                square_weight['atk'][chess.WHITE][chess.square(j,i)] = wa[chess.WHITE][i][j]/float(WA)
                square_weight['atk'][chess.BLACK][chess.square(j,i)] = wa[chess.BLACK][i][j]/float(WA)

        self.square_weight = square_weight

        pass




