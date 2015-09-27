from irc import bot
from irc import strings
from .print_helper import *
from .defiance import Defiance, RuleException

class DefianceBot(bot.SingleServerIRCBot):
    
    def __init__(self, channel, nick, server, port, **params):
        super(DefianceBot, self).__init__([(server, port)], nick, 'github.com/PolarPayne/DefianceBot', reconnection_interval=60, **params)
        self.channel = channel
        self.game = Defiance()
        self.participants = set()
        self.game_in_progress = False
        self.paramless_commands = {
            'disconnect':self.disconnect,
            'die': self.die,
            'participants': self.list_participants,
            'start':self.start_game,
            'end':self.end_game,
            'rainbow' : self.rainbow,
            'table': self.table,
            'test':self.test,
            'ldr': self.make_leader
        }
        self.commands = {
            'hi':self.say_hi,
            'join': self.join_game,
            'leave': self.leave,
            'quit': self.quit,
            'team': self.select_team,
            'approve': self._team_vote(True),
            'reject': self._team_vote(False)
        }

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + '_')

    def on_welcome(self, c, e):
        c.join(self.channel)

    # connection, event
    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0].split(' ')[0])

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]
        if msg[0] == '!':
            cmd = msg.split(' ')[0][1:]
            self.do_command(e, cmd)
        if self.connection.get_nickname() in msg:
            c.privmsg(self.channel, "%s, you talkin' to me?" % (e.source.nick))

    def set_topic(self, new_topic):
        self.connection.topic(self.channel, new_topic)

    def say_hi(self, connection, event):
        human = Person.get_person(event)
        human.talk_to(connection, "hello!")

    def start_game(self):
        try:
            self.game.start()
        except RuleException as ex:
            self.say_to_all(self.connection, str(ex))
            return
        self.say_to_all(self.connection, 'Let the games begin! I will give each of you your roles in private')
        self.table()
        for player in self.game.player_places:
            if self.game.players[player]: 
                pass #human.talk_to(self.connection, "You're a spy!")
            else:
                pass #human.talk_to(self.connection, 'You are with the resistance')

        self.game_in_progress = True

    def rainbow(self):
        self.say_to_all(self.connection, '\x035RA\x038I\x033N\x032B\x036OW')

    def table(self):
        players = self.game.player_places
        if players is None:
            return
        table = draw_table(players) 
        for line in table:
            line = self._show_colors(line+' ', players)
            self.say_to_all(self.connection, line)

    def _show_colors(self, line, players):
        for p in players:
            if p not in line:
                continue
            if self.game.players[p]:
                color = '\x035'
            else:
                color = '\x032'
            reset = '\x03'
            l,r = line.split(p) 
            line = (l + color + p + reset + r)
        return line

    def end_game(self):
        winner = 'resistance' # game.winner or sth
        self.game_in_progress = False
        self.say_to_all(self.connection, 'The %s has won!' % (winner))
        self.participants = set() 
        del self.game
        self.game = Defiance()

    def test(self):
        for name in ['paras', 'VoxWave', 'delma', 'someguy', 'spy', 'six', 'seven']:
            self.game.add_player(name)

    def make_leader(self):
        self.game.leader = 'ZnO'
        self.connection.privmsg(self.channel, 'Oukidouki!')

    def join_game(self, c, e):
        human = Person.get_person(e)
        try:
            self.game.add_player(human.nick)
            self.participants.add(human)
            msg = '{}: you are in the game.'.format(human.nick)
            self.say_to_all(c, msg)
            if len(self.participants) == 10:
                self.start_game()
        except RuleException as ex:
            if str(ex) == 'Wrong state.':
                human.talk_to(c, 'The game is in progress cannot join')
            else:
                human.talk_to(c, 'You are already in the game')

    def select_team(self, c, e):
        human = Person.get_person(e)
        team_members = e.arguments[0].split(' ')[1:]
        try:
            self.game.select_team(human.nick, team_members)
            team = ' '.join(team_members)
            self.say_to_all(c, 'The suggested team is: {}'.format(team))
            self.say_to_all(c, 'Please vote for approval or disproval of this team')
        except RuleException as ex:
            self.say_to_all(c, str(ex))

    def _team_vote(self, approve):
        def vote(c, e):
            human = Person.get_person(e)
            self.game.team_vote(human.nick, approve)
        return vote

    def leave(self, c, e):
        human = Person.get_person(e)
        if self.game_in_progress:
            human.talk_to(c, 'Are you sure you want to leave an ongoing game? If so, command "quit"')
        else:
            self.participants.remove(human)
            self.say_to_all(c, '%s has left the game' % (human.nick))

    def quit(self, c, e):
        human = Person.get_person(e)
        if self.game_in_progress:
            pass
        self.participants.remove(human)
        self.say_to_all(c, '%s has left the game' % (human.nick))

    def list_participants(self):
        players = self.game.player_places
        if not players:
            self.connection.privmsg(self.channel, "There are no participants")
        else:
            output = ', '.join(map(lambda p:p.nick, players))
            self.connection.privmsg(self.channel, output)

    def say_to_all(self, connection, message):
        connection.privmsg(self.channel, message)

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd in self.paramless_commands:
            self.paramless_commands[cmd]()
        elif cmd in self.commands:
            self.commands[cmd](c, e)
        else:
            reply = '%s: Syötit roskaa kutale!' % (nick) #shout-out to Putkamon
            c.privmsg(self.channel, reply)

class Person(object):
    '''A class to represent a person on the channel / in the game.
    Eventually, people will be identified better than by just comparing nicks'''

    @staticmethod
    def get_person(event):
        return Person(event.source.nick)

    def __init__(self, nick):
        self.nick = nick
        self.role = None

    def __eq__(self, person):
        # TODO switch to more accurate algorithm
        if type(person) != type(self):
            return False
        return self.nick == person.nick

    def __hash__(self):
        return hash(self.nick)

    def talk_to(self, connection, message):
        connection.privmsg(self.nick, message)

