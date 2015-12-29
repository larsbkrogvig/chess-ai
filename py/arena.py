import sys
import os
import json
import chess
from time import sleep, time
from datetime import datetime, timedelta
from random import random, choice

# Bots
import random_bot
import basic_bot_1_0
import basic_bot_1_11

dev = False

### Functions

def get_config(board, me):
    cmap = {
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

    return cmap[(result,turn_color[me])]

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

### Parameters

turn_color = {
    True:'WHITE',
    False:'BLACK',
    None: None
}

def new_state():
    state = {
        'played_since': '',
        'fen':          '',
        'turn_desc':    '',
        'W_win':         0,
        'W_draw':        0,
        'W_lose':        0,
        'B_win':         0,
        'B_draw':        0,
        'B_lose' :       0
    }
    return state

def init_state():
    state = None
    if os.path.exists('../html/state'):
        with open('../html/state', 'r') as f:
            state = json.loads(f.read())
    if not state:
        state = new_state()
    return state

def write_state(state):
    with open('../html/state', 'w') as f:
        f.write(json.dumps(state, indent=4))
    pass

state = init_state()

# The Arena
me_bot = basic_bot_1_11
he_bot = random_bot
players = [chess.WHITE, chess.BLACK]
min_turn_time = 1


# In[ ]:
if not state['played_since']:
    state['played_since'] = (datetime.fromtimestamp(time())+timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

while True:
    
    board = chess.Board() # Set up the board
    me    = choice(players)  # My color
    turn  = 0

    cpu_time = {chess.WHITE: 0, chess.BLACK: 0}

    state['fen'] = board.fen()
    if me == chess.WHITE:
        state['player_white'] = me_bot.name()
        state['player_black'] = he_bot.name()
    else:
        state['player_white'] = he_bot.name()
        state['player_black'] = me_bot.name()

    while not board.is_game_over():
        
        t0 = time()
        turn+=1

        tt = time()
        if board.turn == me:
            state['turn_desc'] = str(1+turn/2) + ' - ' + turn_color[not board.turn] + ' to move'
            move = me_bot.move(board) # My move!
        else:
            state['turn_desc'] = str(1+turn/2) + ' - ' + turn_color[not board.turn] + ' to move'
            move = he_bot.move(board) # My opponent's move
        ct = time() - tt
        cpu_time[board.turn] += ct

        board.push(move) # Make the move

        state['fen'] = board.fen()

        if dev: print board

        t1 = time()
        if t1-t0 < min_turn_time:
            sleep(min_turn_time - (t1-t0))

        write_state(state)
    
    state['fen'] = board.fen()
    state['game_desc'] = get_status(board)

    result = None
    if board.is_checkmate(): 
        result = turn_color[not board.turn]

    state[get_config(board, me)] += 1

    write_state(state)

    log_entry = {
        'move_stack': ','.join([str(move) for move in board.move_stack]),
        'winner': turn_color[not board.turn] if board.is_checkmate() else None,
        'white': {
            'bot': me_bot.name if me == chess.WHITE else he_bot.name,
            'cpu_time': cpu_time[chess.WHITE]
            },
        'black': {
            'bot': me_bot.name if me == chess.BLACK else he_bot.name,
            'cpu_time': cpu_time[chess.BLACK]
            },
        }

    sleep(8)

