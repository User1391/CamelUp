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
        # Copy initial board state (list of camel stacks per space)
        self.board = [list(space) for space in board_state]

        # Initialize token board to specified or all None
        if token_board is not None:
            self.token_board = list(token_board) + [None] * (TOT_SPACES - len(token_board))
        else:
            self.token_board = [None] * TOT_SPACES

        # Track how often a camel hits a token
        self.token_land_count = [0] * TOT_SPACES

        # Dice available for this leg
        self.free_dice = set(free_dice) if free_dice is not None else set(Camel)

        # Leg-bet cards available
        self.free_cards = set(free_cards) if free_cards is not None else {(camel, bet) for camel in Camel for bet in Bet}

    def print_board(self):
        print(self.board)

    def dice_left(self):
        return bool(self.free_dice)

    def place_token(self, space, token):
        if space < 0 or space >= TOT_SPACES:
            return False
        # Can't place on occupied space
        if space < len(self.board) and self.board[space]:
            return False
        # Neighbors must be free of tokens
        for neigh in (space-1, space, space+1):
            if 0 <= neigh < TOT_SPACES and self.token_board[neigh] is not None:
                return False
        self.token_board[space] = token
        return True

    def take_leg_card(self, camel, bet):
        if (camel, bet) in self.free_cards:
            self.free_cards.remove((camel, bet))
            return True
        return False

    def eval_game_state(self):
        # Flatten board stacks, then reverse for finish order
        flat = []
        for stack in self.board:
            flat.extend(stack)
        return list(reversed(flat))

    def calculate_outcome(self):
        finish = self.eval_game_state()
        result = {}
        for camel in Camel:
            for bet in Bet:
                if camel == finish[0]:
                    result[(camel, bet)] = bet.value
                elif camel == finish[1]:
                    result[(camel, bet)] = 1
                else:
                    result[(camel, bet)] = -1
        return result

    def move_camel(self, camel, num_spaces):
        # Find and remove the camel (and any above it)
        orig = None
        for idx, stack in enumerate(self.board):
            if camel in stack:
                orig = idx
                pos = stack.index(camel)
                moving = stack[pos:]
                self.board[idx] = stack[:pos]
                break
        if orig is None:
            return

        # Determine landing index
        dest = orig + num_spaces
        # Token effect
        if 0 <= dest < TOT_SPACES and self.token_board[dest] is not None:
            self.token_land_count[dest] += 1
            dest = dest + 1 if self.token_board[dest] == Token.PLUS else dest - 1
        # Clamp
        dest = max(0, dest)
        # Ensure board list is long enough
        while len(self.board) <= dest:
            self.board.append([])
        # Place moving stack
        self.board[dest].extend(moving)

    def roll(self):
        choice = random.choice(tuple(self.free_dice))
        self.free_dice.remove(choice)
        steps = random.randint(1, 3)
        self.move_camel(choice, steps)

    def monte_carlo_eval_raw(self, iterations=100000):
        stats = {c: [0,0,0] for c in Camel}
        for _ in range(iterations):
            sim = copy.deepcopy(self)
            while sim.dice_left():
                sim.roll()
            finish = sim.eval_game_state()
            stats[finish[0]][0] += 1
            stats[finish[1]][1] += 1
            for loser in finish[2:]:
                stats[loser][2] += 1
        return {c: (w/(w+s+l), s/(w+s+l), l/(w+s+l)) for c, (w,s,l) in stats.items()}

    def leg_bet_ev_mc(self, iterations=100000):
        odds = self.monte_carlo_eval_raw(iterations)
        return {(c, b): b.value*odds[c][0] + odds[c][1] - odds[c][2] for c, b in self.free_cards}

    def token_ev_mc(self, iterations=1000):
        ev = {}
        for space in range(TOT_SPACES):
            for tk in (Token.MINUS, Token.PLUS):
                if not self.place_token(space, tk):
                    ev[(space, tk)] = float('-inf')
                    continue
                count = 0
                for _ in range(iterations):
                    sim = copy.deepcopy(self)
                    while sim.dice_left(): sim.roll()
                    count += sim.token_land_count[space]
                ev[(space, tk)] = count / iterations
        return ev

    def best_move(self):
        leg = self.leg_bet_ev_mc()
        tok = self.token_ev_mc()
        best_leg = max(leg.items(), key=lambda x: x[1])
        best_tok = max(tok.items(), key=lambda x: x[1])
        if best_leg[1] <= 1 and best_tok[1] <= 1:
            return ("roll_die",)
        return ("leg_bet", *best_leg[0], best_leg[1]) if best_leg[1] >= best_tok[1] else ("token", *best_tok[0], best_tok[1])

    def choose_move(self):
        mv = self.best_move()
        if mv[0] == "roll_die":
            print("Roll the die and get your coin.")
        elif mv[0] == "leg_bet":
            _, c, b, val = mv
            print(f"Place a leg bet of {b.name} on {c.name} (EV={val:.3f})")
        else:
            _, space, tk, val = mv
            print(f"Place a {tk.name} token on space {space} (EV={val:.3f})")

# Example usage and simple tests
if __name__ == "__main__":
    board_state = [[Camel.YELLOW, Camel.ORANGE], [Camel.BLUE, Camel.GREEN], [Camel.WHITE]]
    token_state = [None, None, None, Token.MINUS]
    gs = GameState(board_state, token_state)

    # Best move
    gs.choose_move()

    # Win/Second/Loss percentages
    odds = gs.monte_carlo_eval_raw(100000)
    print("Win/Second/Loss percentages (approx):")
    for camel, (w, s, l) in odds.items():
        print(f"{camel.name}: Win {w*100:.1f}%, 2nd {s*100:.1f}%, Lose {l*100:.1f}%")

    # Simple sanity tests
    # Test eval_game_state order
    gs2 = GameState([[Camel.YELLOW], [Camel.BLUE], [Camel.ORANGE]])
    assert gs2.eval_game_state() == [Camel.ORANGE, Camel.BLUE, Camel.YELLOW]

    # Test place_token invalid/valid
    assert not gs2.place_token(0, Token.PLUS)  # occupied by YELLOW
    assert gs2.place_token(3, Token.MINUS)

    print("All tests passed.")

