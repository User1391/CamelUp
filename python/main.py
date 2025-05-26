import camelstructures as cs

board_state = [[cs.Camel.YELLOW, cs.Camel.ORANGE], [cs.Camel.WHITE, cs.Camel.BLUE, cs.Camel.GREEN]]
gs = cs.GameState(board_state)

print(gs.eval_game_state())
print("")
print(gs.calculate_outcome())
print("")
gs.move_camel(cs.Camel.YELLOW, 2)
print(gs.eval_game_state())
