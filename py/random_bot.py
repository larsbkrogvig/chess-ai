import chess
import random

class ChessBot(object):

    def __init__(self, r=0.05):
        """Return a new ChessBot object"""
        self.name = 'random_bot'

    def move(self, inboard):
    	return random.choice(list(inboard.legal_moves))
