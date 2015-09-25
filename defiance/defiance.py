import random
from enum import Enum

class RuleException(Exception):
    pass

class States(Enum):
    NOT_STARTED = 0
    TEAM_SELECTION = 1
    TEAM_VOTE = 2

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
        self.state = States.NOT_STARTED
        self.leader = None
        self.team = []
        self.votes = {}

    def add_player(self, nick):
        if self.state is not States.NOT_STARTED:
            raise RuleException("Wrong state.")
        for i in self.players:
            if i.nick == nick:
                raise RuleException("Player {} already in game.".format(nick))
        self.players.append(Player(nick))
        
    def remove_player(self, nick):
        if self.state is not States.NOT_STARTED:
            raise RuleException("Wrong state.")
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
        self.state = States.TEAM_SELECTION
    
    def select_team(self, leader, team):
        if self.state is not States.TEAM_SELECTION:
            raise RuleException("Wrong state.")
        if self.leader != leader:
            raise RuleException("{}.nick is not the leader.".format(leader))
        if len(team) != len(list(set(team2))):
            raise RuleException("All team members must be different.")
        if len(team) != missions[self.state[0]][len(self.players)]:
            raise RuleException("Wrong number of team members.")
        self.team = team
        self.state = States.TEAM_VOTE

    def team_vote(self, nick, vote):
        if self.state is not States.TEAM_VOTE:
            raise RuleException("Wrong state.")
        if nick not in self.players:
            raise RuleException("{} is not a player in this game.".format(nick))
        self.votes[nick] = vote
     
    def end_team_vote(self):
        if self.state is not States.TEAM_VOTE:
            raise RuleException("Wrong state.")
        s = 0
        for i in self.votes:
            if i:
                s += 1
        #All players who didn't voted, voted approve
        s += len(self.players) - len(self.votes)

        if s > len(self.players) // 2:
            state = States.MISSION
        else:
            self.votes = {}
            self.team = None
            self.state = States.TEAM_SELECTION

if __name__ == "__main__":
    game = Defiance()
    players = ["payne", "coolness", "zno", "delma", "voxwave", "harrowed", "serdion"]
    for i in players:
        game.add_player(i)

    print(game.players)
    game.start()
    print(game.players)
    
    game.select_team(game.leader.nick, [])
