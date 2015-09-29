from defiance import players_in_mission
from game.exceptions import RuleException
from game.states import States


class Votes:
    def __init__(self):
        pass

    def add(self, player, vote):
        pass

    def passed(self):
        pass


class Mission:
    def __init__(self):
        self.vote = 0
        self.votes = []
        for i in range(5):
            self.votes.append(Votes())

    def vote(self, player, vote):
        self.current_vote().add(player, vote)

    def current_vote(self):
        return self.votes[self.vote]


class Board:
    def __init__(self, table):
        self.table = table
        self.mission = 0
        self.missions = []
        for i in range(5):
            self.missions.append(Mission(players_in_mission(i, len(self.table))))

    def select_team(self, team):
        if len(team) != len(list(set(team))):
            raise RuleException("All team members must be different.")
        if len(team) != players_in_mission(self.mission, len(self.table)):
            raise RuleException(
                "Wrong number of team members, should be {}.".format(players_in_mission(self.mission, len(self.table))))
        if not set(team).issubset(set(self.table.players)):
            raise RuleException("Some team members are not in this game")

        self.missions[self.mission] = Mission(self.table.leader, team)

    def current_mission(self):
        return self.missions[self.mission]

    def vote_team(self, voter, vote):
        self.current_mission().vote(voter, vote)

    def end_team_vote(self):
        if self.current_mission().vote_track > 5:
            return States.SPY_VICTORY
        elif self.mission_approved():
            self.mission += 1
            return States.ON_MISSION
        else:
            self.current_mission().vote_track += 1
            return States.TEAM_SELECTION
