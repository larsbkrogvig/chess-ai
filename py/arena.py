
import chess
import json
import time
import datetime
import random

# Bots
import random_bot
import basic_bot_1_2


class ChessArena(object):

    def __init__(self, bot1, bot2, seed=None):
        '''Initialize the chess arena with bot modules bot1 and bot2'''
        self.arena_start_time = (datetime.datetime.fromtimestamp(time.time())+datetime.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        self.game_count = 0
        self.game_start_time = None
        self.board = None
        self.player = None
        self.bot1 = bot1
        self.bot2 = bot2
        self.me = None
        self.state = {
            'fen': None,
            'player_white': None,
            'player_black': None,
            'winner': None,
            'desc': None,
            'W_win': 0,
            'W_draw': 0,
            'W_lose': 0,
            'B_win': 0,
            'B_draw': 0,
            'B_lose' : 0
        }

        # Seed if a seed is supplied
        if seed:
            random.seed(seed)

    def wait_for_sync(self):
        '''Wait for the number of seconds since the game started to become integer'''
        time.sleep( (self.game_start_time - time.time()) % 1 )

    def post_state(self):
        '''Writes a json file with the current state to poll'''

        # Write the position state
        self.state['fen'] = self.board.fen()

        fullmove_number = self.board.fullmove_number

        # Write desc 
        if not self.board.is_game_over():
            #Turn and player if the game is ongoing
            self.state['desc'] = 'Turn %i, %s to move' % (fullmove_number, 'WHITE' if self.board.turn else 'BLACK')
        
        elif self.board.is_checkmate():
            # Winner of the game if checkmate
            self.state['desc'] = 'Turn %i, Game over! %s wins!' % (fullmove_number, 'WHITE' if not self.board.turn else 'BLACK')
            self.state['winner'] = (not self.board.turn)

        else:
            # Draw if draw, no reason given
            self.state['desc'] = 'Turn %i, Draw!' % fullmove_number
            self.state['winner'] = None

        with open('../html/state', 'w') as f:
            f.write(json.dumps(self.state, indent=4))

    def make_move(self):
        '''Gets a move from the current player and pushes it to the board'''

        # Have the current player return a move 
        move = self.player[self.board.turn].move(self.board)

        # Push the move on the arena
        self.board.push(move)


    def game_is_ongoing(self):
        '''Return True if a game is onging, False if not'''
        return not self.board.is_game_over()

    def new_game(self):
        '''Initialize a new game'''

        # New board
        self.board = chess.Board()
        self.turn = 1
        self.game_start_time = time.time()

        # Set player randomly
        if random.choice([True, False]):
            self.me = chess.WHITE
            self.player = {
                chess.WHITE: self.bot1.ChessBot(),
                chess.BLACK: self.bot2.ChessBot()
            }
        else:
            self.me = chess.BLACK
            self.player = {
                chess.WHITE: self.bot2.ChessBot(),
                chess.BLACK: self.bot1.ChessBot()
            }

        # Write the names to the state object
        self.state['player_white'] = self.player[chess.WHITE].name
        self.state['player_black'] = self.player[chess.BLACK].name
        self.state['winner'] = None

    def log_draw_reason(self):
        '''Logs the reason of a draw for manual inspection'''

        if self.board.is_stalemate(): 
            reason = 'Stalemate.'
        elif self.board.is_insufficient_material(): 
            reason = 'Insufficient material.', 
        elif self.board.is_seventyfive_moves(): 
            reason = 'Seventyfive moves without capture or pawn move.'
        elif self.board.is_fivefold_repetition(): 
            reason = 'Fivefold repetition.'
        else:
            reason = 'Unknown reason for draw?'

        log_entry = {
            'reason': reason,
            'move_stack': ','.join([str(move) for move in self.board.move_stack])
        }

        with open('../log/%i_draw' % self.game_count, 'w') as f:
            f.write(json.dumps(log_entry, indent=4))

    def update_result_statistics(self):
        '''Count the game and update the result statistics in self.state'''

        self.game_count += 1 # Count the game

        # Get state key
        shorthand_color = 'W' if self.me==chess.WHITE else 'B' 

        if self.state['winner'] == self.me:
            # "I" win
            result = '%s_win' % shorthand_color 

        elif self.state['winner'] == (not self.me):
            # "I" lose
            result = '%s_lose' % shorthand_color

        else:
            # "I" drew
            result = '%s_draw' % shorthand_color

            # Make sure to log the reason for the draw!
            self.log_draw_reason()

        # Increment result counter
        self.state[result] += 1

        # Post the update of the counter
        self.post_state()

def main():

    # Set the players
    player1 = random_bot
    player2 = basic_bot_1_2

    # Initialize the arena
    arena = ChessArena(player2, player2)

    # Play games indefinetly
    while True:

        arena.new_game() # Start a new game

        while arena.game_is_ongoing(): # Play the game

            arena.make_move() # Have the current player make a move
            arena.post_state() # Write a json of the current state
            arena.wait_for_sync() # Wait for the next full second

        # Update statustics
        arena.update_result_statistics()

        # Pause for a few seconds before starting a new game
        time.sleep(6)

    pass

if __name__ == '__main__':
    main()



