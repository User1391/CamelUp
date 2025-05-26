import camelstructures as cs

board_state = [[],[cs.Camel.YELLOW, cs.Camel.ORANGE, cs.Camel.WHITE, cs.Camel.BLUE, cs.Camel.GREEN]]
gs = cs.GameState(board_state)

print(gs.eval_game_state())

print(gs.calculate_outcome())
