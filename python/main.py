import camelstructures as cs

board_state = [[cs.Camel.YELLOW, cs.Camel.ORANGE, cs.Camel.WHITE], [cs.Camel.BLUE, cs.Camel.GREEN]]
token_state = [None, None, cs.Token.MINUS]
gs = cs.GameState(board_state, token_state)


gs.choose_move()
