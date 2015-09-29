from collections import Counter

from game.exceptions import RuleException, StateException
from game.states import States
from game.table import Table
from game.board import Board


def spies_in_game(mission):
    return _spies[mission]
_spies = {5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4}


def players_in_mission(mission, players):
    return _missions[mission][players]
_missions = [{5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3},
             {5: 3, 6: 3, 7: 3, 8: 4, 9: 4, 10: 4},
             {5: 2, 6: 4, 7: 3, 8: 4, 9: 4, 10: 4},
             {5: 3, 6: 3, 7: 4, 8: 5, 9: 5, 10: 5},
             {5: 3, 6: 4, 7: 4, 8: 5, 9: 5, 10: 5}]


def is_double_fail_mission(mission, players):
    return _double_fail[mission][players]
_double_fail = [{5: False, 6: False, 7: False, 8: False, 9: False, 10: False},
                {5: False, 6: False, 7: False, 8: False, 9: False, 10: False},
                {5: False, 6: False, 7: False, 8: False, 9: False, 10: False},
                {5: False, 6: False, 7: True, 8: True, 9: True, 10: True},
                {5: False, 6: False, 7: False, 8: False, 9: False, 10: False}]


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