
# coding: utf-8

# In[1]:

import sys
import chess
from time import sleep
from random import random, choice


# # Search move

# In[1]:

def name():
	return "random"

def move(b, show=False):
    if show: print "Random move."
    return choice(list(b.legal_moves))

def eval_board(b):
    return 0

