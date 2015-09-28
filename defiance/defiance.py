import random
from enum import Enum

class RuleException(Exception):
    pass

class StateException(Exception):
    pass

class States(Enum):
    NOT_STARTED = 0
    TEAM_SELECTION = 1
    TEAM_VOTE = 2
    SPY_VICTORY = 10
    RESISTANCE_VICTORY = 11

spies = {5:2, 6:2, 7:3, 8:3, 9:3, 10:4}
missions = [{5:2, 6:2, 7:2, 8:3, 9:3, 10:3},
            {5:3, 6:3, 7:3, 8:4, 9:4, 10:4},
            {5:2, 6:4, 7:3, 8:4, 9:4, 10:4},
            {5:3, 6:3, 7:4, 8:5, 9:5, 10:5},
            {5:3, 6:4, 7:4, 8:5, 9:5, 10:5}]
double_fail = [{5:False, 6:False, 7:False, 8:False, 9:False, 10:False},
	       {5:False, 6:False, 7:False, 8:False, 9:False, 10:False},
               {5:False, 6:False, 7:False, 8:False, 9:False, 10:False},
               {5:False, 6:False, 7:True, 8:True, 9:True, 10:True},
               {5:False, 6:False, 7:False, 8:False, 9:False, 10:False}]

class Defiance:
    def __init__(self):
        self.players = {}
        self.state = States.NOT_STARTED
        self.leader = None
        self.team = []
        self.votes = {}
        self.round_number = 0
        self.player_places = []
        self.vote_tracker = 0
        self.current_mission = 0
        self.mission = {}

    def add_player(self, nick):
        if self.state is not States.NOT_STARTED:
            raise RuleException("Wrong state.")
        if nick in self.players:
            raise RuleException("{} is already in the game.".format(nick))
        self.players[nick] = False
        
    def remove_player(self, nick):
        if self.state is not States.NOT_STARTED:
            raise RuleException("Wrong state.")
        if nick not in self.players:
            raise RuleException("{} is not in the game, and cannot be removed.".format(nick))
        del self.players[nick]

    def start(self):
        if len(self.players) < 5:
            raise RuleException("Not enough players (min 5).")
        if len(self.players) > 10:
            raise RuleException("Too many players (max 10).")

        self.player_places = list(self.players.keys())
        random.shuffle(self.player_places)
        for i in range(spies[len(self.player_places)]):
            self.players[self.player_places[i]] = True
        random.shuffle(self.player_places)
        self.leader = self.player_places[0]
        self.state = States.TEAM_SELECTION
    
    def select_team(self, leader, team):
        if self.state is not States.TEAM_SELECTION:
            raise RuleException("Wrong state.")
        if self.leader != leader:
            raise RuleException("{}.nick is not the leader.".format(leader))
        if len(team) != len(list(set(team))):
            raise RuleException("All team members must be different.")
        if len(team) != missions[self.round_number][len(self.players)]:
            raise RuleException("Wrong number of team members.")
        if not set(team).issubset(set(self.players.keys())):
            raise RuleException("Some team members are not in this game")
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
            self.vote_tracker = 0
            self.votes = {}
        else:
            self.votes = {}
            self.team = None
            self.vote_tracker += 1
            self.state = States.TEAM_SELECTION
        if self.vote_tracker > 5:
            self.state = States.SPY_VICTORY

    def play_mission(self, nick, play):
        """False is failure, True is success."""
        if self.state is not States.MISSION:
            raise RuleException("Wrong state.")
        if nick not in self.players:
            raise RuleException("{} not in game.")
        if nick not in self.team:
            raise RuleException("{} not in the team.")
        if not self.players[nick] and not play:
            raise RuleException("A non spy must not play a failure.")
        self.votes[nick] = play

    def end_mission(self):
        if self.state is not States.MISSION:
            raise RuleException("Wrong state.")
        c = Counter(self.votes.values())
	if (not double_fail[self.current_mission][len(self.players)] and c[False] > 0) or (double_fail[self.current_mission][len(self.players)] and c[False] > 1):
            self.mission[self.current_mission] = False
        else:
            self.mission[self.current_mission] = True
        self.current_mission += 1
        self.state = States.TEAM_SELECTION

if __name__ == "__main__":
    game = Defiance()
    players = ["payne", "coolness", "zno", "delma", "voxwave", "harrowed", "serdion"]
    for i in players:
        game.add_player(i)
    game.start()    
    game.select_team(game.leader, ["töttöröö", "kissa"])
