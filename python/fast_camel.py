from enum import IntEnum
import random

TOT_SPACES = 16

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Camel(IntEnum):
    YELLOW = 1
    ORANGE = 2
    WHITE = 3
    BLUE = 4
    GREEN = 5

class Token(IntEnum):
    PLUS = 1
    MINUS = 2

class Bet(IntEnum):
    FIVE = 5
    THREE = 3
    TWO = 2

class GameState:
    __slots__ = (
        'board', 'token_board', 'token_land_count',
        'free_dice', 'free_cards'
    )

    def __init__(self, board_state, token_board=None, free_dice=None, free_cards=None):
        self.board = [list(space) for space in board_state]
        self.token_board = (
            list(token_board) + [None] * (TOT_SPACES - len(token_board))
            if token_board is not None else [None] * TOT_SPACES
        )
        self.token_land_count = [0] * TOT_SPACES
        self.free_dice = list(free_dice) if free_dice is not None else [c for c in Camel]
        self.free_cards = (
            set(free_cards) if free_cards is not None
            else {(camel, bet) for camel in Camel for bet in Bet}
        )

    def clone(self):
        gs = GameState.__new__(GameState)
        gs.board = [stack.copy() for stack in self.board]
        gs.token_board = self.token_board.copy()
        gs.token_land_count = self.token_land_count.copy()
        gs.free_dice = self.free_dice.copy()
        gs.free_cards = self.free_cards.copy()
        return gs

    def dice_left(self):
        return bool(self.free_dice)

    def place_token(self, space, token):
        if not (0 <= space < TOT_SPACES):
            return False
        if space < len(self.board) and self.board[space]:
            return False
        for neigh in (space - 1, space, space + 1):
            if 0 <= neigh < TOT_SPACES and self.token_board[neigh] is not None:
                return False
        self.token_board[space] = token
        return True

    def eval_game_state(self):
        flat = []
        for stack in self.board:
            flat.extend(stack)
        flat.reverse()
        return flat

    def calculate_outcome(self):
        finish = self.eval_game_state()
        res = {}
        winner, runner_up = finish[0], finish[1]
        for camel in Camel:
            for bet in Bet:
                if camel == winner:
                    res[(camel, bet)] = bet
                elif camel == runner_up:
                    res[(camel, bet)] = 1
                else:
                    res[(camel, bet)] = -1
        return res

    def move_camel(self, camel, num_spaces):
        # find and detach
        for idx, stack in enumerate(self.board):
            if camel in stack:
                pos = stack.index(camel)
                moving = stack[pos:]
                self.board[idx] = stack[:pos]
                break
        else:
            return
        dest = idx + num_spaces
        token = self.token_board[dest] if 0 <= dest < TOT_SPACES else None
        if token is not None:
            self.token_land_count[dest] += 1
            dest += 1 if token == Token.PLUS else -1
        dest = max(0, dest)
        while len(self.board) <= dest:
            self.board.append([])
        self.board[dest].extend(moving)

    def roll(self):
        # O(1) die selection and removal
        dice = self.free_dice
        i = random.randrange(len(dice))
        choice = dice.pop(i)
        steps = random.randint(1, 3)
        self.move_camel(choice, steps)

    def monte_carlo_eval_raw(self, iterations=100000):
        stats = {c: [0,0,0] for c in Camel}
        for _ in range(iterations):
            sim = self.clone()
            while sim.dice_left():
                sim.roll()
            finish = sim.eval_game_state()
            stats[finish[0]][0] += 1
            stats[finish[1]][1] += 1
            for loser in finish[2:]:
                stats[loser][2] += 1
        return {c: (w/(w+s+l), s/(w+s+l), l/(w+s+l))
                for c, (w,s,l) in stats.items()}

    def leg_bet_ev_mc(self, iterations=100000):
        odds = self.monte_carlo_eval_raw(iterations)
        return {(c, b): b * odds[c][0] + odds[c][1] - odds[c][2]
                for (c, b) in self.free_cards}

    def token_ev_mc(self, iterations=10000):
        ev = {}
        base_tokens = list(self.token_board)
        for space in range(TOT_SPACES):
            for tk in (Token.MINUS, Token.PLUS):
                # restore token_board
                self.token_board = base_tokens.copy()
                if not self.place_token(space, tk):
                    ev[(space, tk)] = float('-inf')
                    continue
                count = 0
                for _ in range(iterations):
                    sim = self.clone()
                    while sim.dice_left(): sim.roll()
                    count += sim.token_land_count[space]
                ev[(space, tk)] = count / iterations
        self.token_board = base_tokens
        return ev

    def best_move(self):
        leg, tok = self.leg_bet_ev_mc(), self.token_ev_mc()
        best_leg = max(leg.items(), key=lambda x: x[1])
        best_tok = max(tok.items(), key=lambda x: x[1])
        if best_leg[1] <= 1 and best_tok[1] <= 1:
            return ("roll_die",)
        return ("leg_bet", *best_leg[0], best_leg[1]) if best_leg[1] >= best_tok[1] else ("token", *best_tok[0], best_tok[1])

    def choose_move(self):
        mv = self.best_move()
        if mv[0] == "roll_die":
            print(bcolors.OKCYAN + "Roll the die and get your coin." + bcolors.ENDC)
        elif mv[0] == "leg_bet":
            _, c, b, val = mv
            print(bcolors.OKCYAN + f"Place a leg bet of {b.name} on {c.name} (EV={val:.3f})" + bcolors.ENDC)
        else:
            _, space, tk, val = mv
            print(bcolors.OKCYAN + f"Place a {tk.name} token on space {space} (EV={val:.3f})" + bcolors.ENDC)

if __name__ == "__main__":
    board_state = [[Camel.YELLOW, Camel.ORANGE], [Camel.BLUE, Camel.GREEN], [Camel.WHITE]]
    token_state = [None, None, None, Token.MINUS]
    gs = GameState(board_state, token_state)
    
    print("")
    # Best move
    gs.choose_move()
    print("")

    # Win/Second/Loss percentages
    odds = gs.monte_carlo_eval_raw(1000000)
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


