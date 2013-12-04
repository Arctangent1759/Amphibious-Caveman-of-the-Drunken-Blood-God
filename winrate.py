numWin=0
total=0
try:
    while True:
        inLine = raw_input()
        total+=1
        if inLine=="Win":
            numWin+=1
except EOFError:
    print "Win rate for Me: ",float(numRed)/float(total)
    print "Win rate for Opp: ",float(total-numRed)/float(total)
