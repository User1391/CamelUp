from enum import Enum
import random

class Camel(Enum):
    YELLOW = 1
    ORANGE = 2
    WHITE = 3
    BLUE = 4
    GREEN = 5

class Token(Enum):
    PLUS = 1
    MINUS = 2

class Bet(Enum):
    FIVE = 5
    THREE = 3
    TWO = 2

class GameState:
    board = []
    token_board = []
    free_dice = {Camel.YELLOW, Camel.ORANGE, Camel.WHITE, Camel.BLUE, Camel.GREEN}
    
    def __init__(self, board_state, token_board=None, free_dice=None, free_cards=None):
        self.board = board_state
        if token_board != None: self.token_board = token_board
        if free_dice != None: self.free_dice = free_dice
        if free_cards != None: self.free_cards = free_cards 
    
    def eval_game_state(self):
        """Return an ordered list of the camels, from first to fifth for the round."""
        output_list = []
        for space in self.board:
            if len(space) != 0:
                for camel in space:
                    if camel in Camel:
                        output_list.append(camel) 
        return output_list[::-1]

    def calculate_outcome(self):
        """Return a dictionary that takes (Camel, Bet) and returns the value of that bet in coins (int)"""
        output_map = {}
        finish = self.eval_game_state()
        for camel in Camel:
            for bet in Bet:
                cam_val = -1
                if camel == finish[0]:
                    cam_val = bet.value
                elif camel == finish[1]:
                    cam_val = 1
                output_map[(camel, bet)] = cam_val 

        return output_map

    def move_camel(self, camel, num_spaces):
        """Move the camel forward the number of desired spaces, while accounting for plus or minus tokens"""
        for space_idx in range(len(self.board)):
            if len(self.board[space_idx]) != 0:
                for camel_idx in range(len(self.board[space_idx])):
                    if self.board[space_idx][camel_idx] == camel:
                        # get sublist of camels from camel we want to move and upwards
                        camel_stack = self.board[space_idx][camel_idx:]
                        # now remove that stack 
                        self.board[space_idx] = self.board[space_idx][:camel_idx]
                        break
            # now, we should check forward to see if a token exists at the spot we want to go
            new_space_idx = space_idx + num_spaces
            if new_space_idx >= len(self.token_board):
                # no token, just create or extend as normal
                # check if the space we're going to even exists 
                if new_space_idx >= len(self.board):
                    self.board.insert(new_space_idx, camel_stack)
                else:
                    self.board[new_space_idx].extend(camel_stack)
            else:
                # make sure it's not just a blank space 
                if self.token_board[new_space_idx] == None:
                    # we know it's blank because camels can never be on the same space as tokens
                    self.board.insert(new_space_idx, camel_stack)
                elif self.token_board[new_space_idx] == Token.PLUS:
                    # do same thing as above but for the next space 
                    if new_space_idx + 1 >= len(self.board):
                        self.board[new_space_idx + 1] = camel_stack
                    else:
                        self.board[new_space_idx + 1].extend(camel_stack)
                else:
                    # we know it's a minus space 
                    self.board[new_space_idx - 1] = camel_stack + self.board[new_space_idx - 1]
            break

