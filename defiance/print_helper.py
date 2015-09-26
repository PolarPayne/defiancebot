t = ['╔═════╗',  
     '║ tkt ║',
     '╚═════╝']

def _top_or_bottom_row(maxlen, player, second_player = None):
    if second_player is None:
        return ('{:^'+str(2*(maxlen+2)+7)+'}').format(player)
    else:
        return ('{:>'+str(maxlen+2+2)+'}').format(player) + '   ' + second_player
        

def _table_row(i, maxlen, player1, player2):
    left_side = ('{:^'+str(maxlen+2)+'}').format(player1)
    right_side = ('{:^'+str(maxlen+2)+'}').format(player2)
    return left_side + t[i] + right_side

def draw_table(players):
    maxlen = len(max(players, key=len))
    if len(players) < 7:
        up_row = _top_or_bottom_row(maxlen, players[-1])
        row1 = _table_row(0, maxlen, players[0], players[-2])
    else:
        up_row = _top_or_bottom_row(maxlen, players[-1], players[-2])
        row1 = _table_row(0, maxlen, players[0], players[-3])

    if len(players) in (6,7):
        bottom_row = _top_or_bottom_row(maxlen, players[2])
        row3 = _table_row(2, maxlen, players[1], players[3])
    elif len(players) == 8:
        bottom_row = _top_or_bottom_row(maxlen, players[2], players[3])
        row3 = _table_row(2, maxlen, players[1], players[4])
    elif len(players) == 9:
        bottom_row = _top_or_bottom_row(maxlen, players[3]) 
        row3 = _table_row(2, maxlen, players[2], players[4])
    elif len(players) == 10:
        bottom_row = _top_or_bottom_row(maxlen, players[3], players[4])
        row3 = _table_row(2, maxlen, players[2], players[5])
    else:
        row3 = _table_row(2, maxlen, players[1], players[2]) 
        bottom_row = ' '

    if len(players) < 9:
        row2 = ' ' * (maxlen+2) + t[1]
    elif len(players) == 9:
        row2 = _table_row(1, maxlen, players[1], players[5])
    else:
        row2 = _table_row(1, maxlen, players[1], players[6])

    lines = [up_row, row1, row2, row3, bottom_row]
    #if bottom_row == '':
    #    lines = lines[:-1]
    return lines   
