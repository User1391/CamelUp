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


    


