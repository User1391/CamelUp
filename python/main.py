import camelstructures as cs

board_state = [[cs.Camel.YELLOW, cs.Camel.ORANGE, cs.Camel.WHITE], [cs.Camel.BLUE, cs.Camel.GREEN]]
token_state = [None, None, cs.Token.MINUS]
die_state = {cs.Camel.YELLOW, cs.Camel.WHITE}
gs = cs.GameState(board_state, token_state, die_state)


print(board_state)
print("")

#mcsim = gs.monte_carlo_eval_raw()
#for camel in cs.Camel: 
#    print(camel.name + " wins " + str(round(mcsim[camel][0]*100)) + "% of the time.")
#    print(camel.name + " gets second " + str(round(mcsim[camel][1]*100)) + "% of the time.")
#    print(camel.name + " loses " + str(round(mcsim[camel][2]*100)) + "% of the time.")
#    print("")

evs = gs.leg_bet_ev_mc()
for camel in cs.Camel:
    for bet in cs.Bet:
        print("Betting on " + camel.name + " with bet " + bet.name + " has an expected outcome of " + str(round(evs[(camel, bet)],2)) + " coins.")
    print("")

tok_ev = gs.token_ev_mc()
for space in range(cs.TOT_SPACES):
    for token in cs.Token:
        print("Placing a " + token.name + " token on space " + str(space) + " nets an ev of " + str(tok_ev[(space, token)]))
    print("")
