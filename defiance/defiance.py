class PlayerAmountException(Exception):
    pass

class Player:
    def __init__(self, nick, spy=None, role=None):
        self.nick = nick
        self.spy = spy
        self.role = role

class Defiance:
    def __init__(self):
        self.players = set()

    def join(self, nick):
        self.players.add(Player(nick))
        if len(self.players) == 10:
            self.start()
        
    def leave(self, nick):
        self.players.remove(Player(nick))
        
    def start(self):
        if len(self.players) < 5:
            raise PlayerAmountException("Not enough players (min 5)")
        if len(self.players) > 10:
            raise PlayerAmounrException("Too many players (max 10)")
        
        #TODO random spies, place players in a "table"
    
    def proceed(self):
        pass
