
# coding: utf-8

# In[ ]:

import sys
import chess
from time import sleep, time
from random import random, choice

# # Bots

# In[ ]:

import random_bot
import final_bot


# ### Parameters

# In[ ]:

turn_color = {
    True:'WHITE',
    False:'BLACK',
    None: None
}


# ### Utility functions

# In[ ]:

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

me_bot = mr_final
he_bot = mr_random
players = [chess.WHITE, chess.BLACK]
min_turn_time = 1


# In[ ]:

while True:
    
    board = chess.Board() # Set up the board
    me = choice(players)  # My color
        
    turn=0
    while not board.is_game_over():
        
        t0 = time()
        turn+=1
        
        with open('../html/fen.txt', 'w') as f:
            f.write(board.fen())
        
        if board.turn == me:
            with open('../html/status.txt', 'w') as f:
                f.write(str(1+turn/2) + ' - My move, ' + turn_color[board.turn])
            move = me_bot.move(board, True) # My move!
        else:
            with open('../html/status.txt', 'w') as f:
                f.write(str(1+turn/2) + ' - His move, ' + turn_color[board.turn])
            move = he_bot.move(board, True) # My opponent's move

        board.push(move) # Make the move

        t1 = time()
        if t1-t0 < min_turn_time:
            sleep(min_turn_time - (t1-t0))
            
    with open('../html/fen.txt', 'w') as f:
            f.write(board.fen())
            
    with open('../html/status.txt', 'w') as f:
        f.write(get_status(board))
        
    sleep(8)
