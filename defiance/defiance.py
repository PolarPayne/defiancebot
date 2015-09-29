import random
from enum import Enum
from collections import Counter


class RuleException(Exception):
    pass


class StateException(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual

    def __str__(self):
        return "State was {}, but it should have been {}.".format(self.actual, self.expected)


class States(Enum):
    NOT_STARTED = 0
    TEAM_SELECTION = 1
    TEAM_VOTE = 2
    ON_MISSION = 3
    SPY_VICTORY = 10
    RESISTANCE_VICTORY = 11


_spies = {5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4}


def spies_in_game(mission):
    return _spies[mission]


_missions = [{5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3},
             {5: 3, 6: 3, 7: 3, 8: 4, 9: 4, 10: 4},
             {5: 2, 6: 4, 7: 3, 8: 4, 9: 4, 10: 4},
             {5: 3, 6: 3, 7: 4, 8: 5, 9: 5, 10: 5},
             {5: 3, 6: 4, 7: 4, 8: 5, 9: 5, 10: 5}]


def players_in_mission(mission, players):
    return _missions[mission][players]


_double_fail = [{5: False, 6: False, 7: False, 8: False, 9: False, 10: False},
                {5: False, 6: False, 7: False, 8: False, 9: False, 10: False},
                {5: False, 6: False, 7: False, 8: False, 9: False, 10: False},
                {5: False, 6: False, 7: True, 8: True, 9: True, 10: True},
                {5: False, 6: False, 7: False, 8: False, 9: False, 10: False}]


def is_double_fail_mission(mission, players):
    return _double_fail[mission][players]


class Player():
    def __init__(self, nick, spy=False):
        self.nick = nick
        self.spy = spy

    def __eq__(self, other):
        if type(self) is not type(other):
            if type(other) is str:
                return self.nick == other
            else:
                return False
        return self.nick == other.nick


class Table:
    def __init__(self):
        self.players = []
        self.leader = None
        self.spies_selected = False
        self.leader_selected = False

    def add(self, nick):
        if len(self) >= 10:
            raise RuleException("There are already 10 players in this game.")
        if nick in self:
            raise RuleException("{} is already in this table.".format(nick))
        self.players.append(nick)
        self._shuffle()

    def remove(self, nick):
        if nick not in self:
            raise RuleException("{} is not in this table.".format(nick))
        self.players.remove(nick)

    def select_spies(self):
        if self.spies_selected:
            raise RuntimeError("Spies were already selected.")
        for i in random.sample(self.players, spies_in_game(len(self.players))):
            i.spy = True
        self.spies_selected = True

    def select_leader(self):
        if self.leader_selected:
            raise RuntimeError("Leader was already selected.")
        self.leader = random.choice(self.players)
        self.leader_selected = True

    def _shuffle(self):
        random.shuffle(self.players)

    def __contains__(self, item):
        return item in self.players

    def __len__(self):
        return len(self.players)


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


class Defiance:
    def __init__(self):
        self.state = States.NOT_STARTED
        self.table = Table()
        self.board = Board(self.table)

    def check_state(self, expected):
        if self.state is not expected:
            raise StateException(expected, self.state)

    def add_player(self, nick):
        self.check_state(States.NOT_STARTED)
        self.table.add(nick)

    def remove_player(self, nick):
        self.check_state(States.NOT_STARTED)
        self.table.remove(nick)

    def start(self):
        self.check_state(States.NOT_STARTED)

        if len(self.table) < 5:
            raise RuleException("Not enough players (min 5).")

        self.table.select_spies()
        self.table.select_leader()

        self.state = States.TEAM_SELECTION

    def select_team(self, leader, team):
        self.check_state(States.TEAM_SELECTION)

        if self.table.leader != leader:
            raise RuleException("Only the leader can choose a team.")

        self.board.select_team(team)

        self.state = States.TEAM_VOTE

    def team_vote(self, nick, vote):
        self.check_state(States.TEAM_VOTE)

        if nick not in self.players:
            raise RuleException("{} is not a player in this game.".format(nick))

        self.board.team_vote(nick, vote)

    def end_team_vote(self):
        self.check_state(States.TEAM_VOTE)

        self.state = self.board.end_team_vote()

    def play_mission(self, nick, play):
        if self.state is not States.ON_MISSION:
            raise RuleException("Wrong state.")
        if nick not in self.players:
            raise RuleException("{} not in game.")
        if nick not in self.team:
            raise RuleException("{} not in the team.")
        if not self.players[nick] and not play:
            raise RuleException("A non spy must not play a failure.")
        self.votes[nick] = play

    def end_mission(self):
        if self.state is not States.ON_MISSION:
            raise RuleException("Wrong state.")
        c = Counter(self.votes.values())
        if (not double_fail[self.current_mission][len(self.players)] and c[False] > 0) or (
                    double_fail[self.current_mission][len(self.players)] and c[False] > 1):
            self.mission[self.current_mission] = False
        else:
            self.mission[self.current_mission] = True

        # check for game end
        c = Counter(self.mission.values())
        if c[False] >= 3:
            self.state = States.SPY_VICTORY
        if c[True] >= 3:
            self.state = States.RESISTANCE_VICTORY

        self.leader = self.next_leader()
        self.current_mission += 1
        self.state = States.TEAM_SELECTION

    def next_leader(self):
        if self.player_places.index(self.leader) + 1 > len(self.player_places):
            return self.player_places[0]
        else:
            return self.player_places[self.player_places.index(self.leader) + 1]


if __name__ == "__main__":
    game = Defiance()
    game.add_player("payne")
    game.remove_player("payne")
