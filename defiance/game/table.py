from defiance import spies_in_game
from game.exceptions import RuleException
import random


class Player:
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
