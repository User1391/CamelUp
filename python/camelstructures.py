from enum import Enum
import random
import copy

TOT_SPACES = 18

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
    
    def __init__(self, board_state, token_board=None, free_dice=None, free_cards=None):
        # board_state is presumably a list-of-lists; copy it if you plan to mutate
        self.board = [list(space) for space in board_state]

        # per‐instance token_board
        if token_board is not None:
            self.token_board = list(token_board) + [None] * (TOT_SPACES - len(token_board))
        else:
            # default: no tokens on any space
            self.token_board = [None] * TOT_SPACES
        
        # use to track when a camel (or camel stack) lands on a token 
        self.token_land_count = [0] * TOT_SPACES

        # per‐instance free_dice
        if free_dice is not None:
            self.free_dice = set(free_dice)
        else:
            # start each new game with all five dice available
            self.free_dice = set(Camel)

        # per‐instance free_cards, if you ever use them
        if free_cards is not None:
            self.free_cards = free_cards
        else:
            self.free_cards = set()
            for camel in Camel:
                for bet in Bet:
                    self.free_cards.add((camel, bet))


    def print_board(self):
        """Prints the board state as-is"""
        print(self.board) 

    def dice_left(self):
        """Returns the Boolean of if any free dice are remaining to roll"""
        return len(self.free_dice) > 0
    
    def place_token(self, space, token):
        """Attempts to place the desired token type on a desired space. Returns True if successfull and False if fails"""
        if space >= len(self.board) or len(self.board[space]) == 0:
            if space - 1 >= len(self.token_board) or self.token_board[space-1] == None:
                if space >= len(self.token_board) or self.token_board[space] == None:
                    if space + 1 >= len(self.token_board) or self.token_board[space+1] == None:
                        if space >= len(self.token_board):
                            self.token_board.extend([None] * (space + 1 - len(self.token_board)))
                        self.token_board[space]  = token
                        return True
        return False

    def take_leg_card(self, camel, bet):
        """Plays the specified leg bet card thereby removing it from the game. Returns True upon success and False if the card was missing"""
        if (camel, bet) in self.free_cards:
            self.free_cards.remove((camel, bet))
            return True
        else:
            return False

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
        camel_stack = None
        for space_idx in range(len(self.board)):
            if len(self.board[space_idx]) != 0:
                for camel_idx in range(len(self.board[space_idx])):
                    if self.board[space_idx][camel_idx] == camel:
                        # get sublist of camels from camel we want to move and upwards
                        camel_stack = self.board[space_idx][camel_idx:]
                        # now remove that stack 
                        self.board[space_idx] = self.board[space_idx][:camel_idx]
                        # print("Camel Stack", camel_stack)
                        break
            if camel_stack != None:
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
                        self.token_land_count[new_space_idx] += 1
                        # do same thing as above but for the next space 
                        if new_space_idx + 1 >= len(self.board):
                            self.board.insert(new_space_idx + 1, camel_stack)
                        else:
                            self.board[new_space_idx + 1].extend(camel_stack)                    
                    else:
                        self.token_land_count[new_space_idx] += 1
                        target = new_space_idx - 1

                        # if you ever land at “space 0” with a minus, push to front
                        if target < 0:
                            self.board.insert(0, camel_stack)

                        # if you land beyond the current end, insert there
                        elif target >= len(self.board):
                            self.board.insert(target, camel_stack)

                        # otherwise just stack onto the existing space
                        else:
                            self.board[target] = camel_stack + self.board[target]
                break

    def roll(self):
        """Rolls a random die from the set of remaining dice and moves that respective camel accordingly"""
        rolled_camel = random.choice(tuple(self.free_dice))
        self.free_dice.remove(rolled_camel)
        die_roll = random.randint(1,3)
        #print("Moved camel " + rolled_camel.name + " for " + str(die_roll) + " spaces.")
        self.move_camel(rolled_camel, die_roll)
    
    def monte_carlo_eval_raw(self, iterations=100000):
        """Does a Monte Carlo evaluation of the current game state and returns the winning, second, and losing odds for each camel"""
        first =  {Camel.YELLOW : 0, Camel.ORANGE : 0, Camel.WHITE : 0, Camel.BLUE : 0, Camel.GREEN : 0}
        second = {Camel.YELLOW : 0, Camel.ORANGE : 0, Camel.WHITE : 0, Camel.BLUE : 0, Camel.GREEN : 0}
        lose = {Camel.YELLOW : 0, Camel.ORANGE : 0, Camel.WHITE : 0, Camel.BLUE : 0, Camel.GREEN : 0}
        
        for i in range(iterations):
            cpy_game = copy.deepcopy(self)
            while cpy_game.dice_left():
                cpy_game.roll()
                #cpy_game.print_board()
            outcome = cpy_game.eval_game_state()
            first[outcome[0]] += 1 
            second[outcome[1]] += 1 
            for cam in outcome[2:]:
                lose[cam] +=1 
            del cpy_game
        
        output = {}
        for camel in Camel:
            tot = first[camel] + second[camel] + lose[camel]
            win_percent = first[camel] / tot 
            second_percent = second[camel] / tot 
            lose_percent = lose[camel] / tot 
            output[camel] = (win_percent, second_percent, lose_percent)
        
        return output
    
    def leg_bet_ev_mc(self, iterations=100000):
        """Returns a dictionary using key (Camel, Bet) and value type float representing the EV in chips calculated using Monte Carlo evaluation"""
        eval = self.monte_carlo_eval_raw(iterations)
        output = {}
        for camel, bet in self.free_cards:
                output[(camel, bet)] = bet.value * eval[camel][0] + eval[camel][1] - eval[camel][2]
            
        return output
    
    def token_ev_mc(self, iterations=1000):
        """Returns a dict giving the ev as a float for each valid token placement space with the token type (space, Token)"""
        outcome = {}
        for space in range(TOT_SPACES):
            for tok in (Token.MINUS, Token.PLUS):
                cnt = 0
                for i in range(iterations):
                    cpy_game = copy.deepcopy(self)
                    if cpy_game.place_token(space, tok):
                        while cpy_game.dice_left():
                            cpy_game.roll()
                        cnt += cpy_game.token_land_count[space]

                    del cpy_game

                outcome[(space, tok)] = cnt / iterations

        return outcome
        
    def best_move(self):
        """Runs the Monte Carlo sims for tokens and leg bets and determines the best move to make.
        Returns either
            ("leg_bet", Camel, Bet, ev)
        or
            ("token", space_index, Token, ev)
        or
            Roll Die  # if all EVs ≤ 1
        """
        # 1) run your two sims
        leg_ev   = self.leg_bet_ev_mc()
        token_ev = self.token_ev_mc()

        # 2) find the best single leg bet
        (best_camel, best_bet), best_leg_ev = max(leg_ev.items(), key=lambda kv: kv[1])
        # 3) find the best single token placement
        (best_space, best_tok), best_tok_ev = max(token_ev.items(), key=lambda kv: kv[1])

        # 4) if neither is positive, roll die
        if best_leg_ev <= 1 and best_tok_ev <= 1:
            return ("roll_die")

        # 5) pick the higher‐EV move
        if best_leg_ev >= best_tok_ev:
            return ("leg_bet", best_camel, best_bet, best_leg_ev)
        else:
            return ("token", best_space, best_tok, best_tok_ev)
    
    def choose_move(self):
        move = self.best_move()
        if move[0] == "roll_die":
            print("Roll the die and get your coin.")
        elif move[0] == "leg_bet":
            _, camel, bet, ev = move
            print(f"Place a leg bet of {bet.name} on {camel.name} (EV={ev:.3f})")
        else:
            _, space, tok, ev = move
            print(f"Place a {tok.name} token on space {space} (EV={ev:.3f})") 
