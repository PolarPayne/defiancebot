import random

class RuleException(Exception):
    pass

class Player:
    def __init__(self, nick, spy=False, role=None):
        self.nick = nick
        self.spy = spy
        self.role = role

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.nick == other.nick

    def __hash__(self):
        return hash(self.nick)

    def __str__(self):
        return "nick=" + self.nick + ";spy=" + str(self.spy)

    def __repr__(self):
        return self.__str__()

spies = {5:2, 6:2, 7:3, 8:3, 9:3, 10:4}
missions = [{5:2, 6:2, 7:2, 8:3, 9:3, 10:3},
            {5:3, 6:3, 7:3, 8:4, 9:4, 10:4},
            {5:2, 6:4, 7:3, 8:4, 9:4, 10:4},
            {5:3, 6:3, 7:4, 8:5, 9:5, 10:5},
            {5:3, 6:4, 7:4, 8:5, 9:5, 10:5}]

class Defiance:
    def __init__(self):
        self.players = []
        self.state = None
        self.leader = None

    def add_player(self, nick):
        for i in self.players:
            if i.nick == nick:
                raise RuleException("Player {} already in game.".format(nick))
        self.players.append(Player(nick))
        
    def remove_player(self, nick):
        for i in self.players:
            if i.nick == nick:
                del self.players[i]
                return True
        return False

    def start(self):
        if len(self.players) < 5:
            raise RuleException("Not enough players (min 5).")
        if len(self.players) > 10:
            raise RuleException("Too many players (max 10).")

        random.shuffle(self.players)
        for i in range(spies[len(self.players)]):
            self.players[i].spy = True
        random.shuffle(self.players)
        self.leader = self.players[0]
        self.state = (0,0)
    
    def select_team(self, leader, team):
        if self.leader != leader:
            raise RuleException("{}.nick is not the leader.".format(leader))
        if len(team) != len(list(set(team2))):
            raise RuleException("All team members must be different.")
        if len(team) != missions[self.state[0]][len(self.players)]:
            raise RuleException("Wrong number of team members.")
        self.team = team

    def vote(self, nick, vote):
        if nick not in self.votes:
            self.votes = Vote(nick, 

if __name__ == "__main__":
    game = Defiance()
    players = ["payne", "coolness", "zno", "delma", "voxwave", "harrowed", "serdion"]
    for i in players:
        game.add_player(i)

    print(game.players)
    game.start()
    print(game.players)
    
    game.select_team(game.leader.nick, [])
