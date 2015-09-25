from irc import bot
from irc import strings

class DefianceBot(bot.SingleServerIRCBot):
    
    def __init__(self, channel, nick, server, port, **params):
        super(DefianceBot, self).__init__([(server, port)], nick, 'github.com/PolarPayne/DefianceBot', reconnection_interval=60, **params)
        self.channel = channel
        self.participants = set()
        self.game_in_progress = False
        self.paramless_commands = {
            'disconnect':self.disconnect,
            'die': self.die,
            'participants': self.list_participants,
            'start':self.start_game,
            'end':self.end_game
        }
        self.commands = {
            'hi':self.say_hi,
            'join': self.join_game
        }

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + '_')

    def on_welcome(self, c, e):
        c.join(self.channel)

    # connection, event
    def on_privmsg(self, c, e):
        #self.do_command(e, e.arguments[0])
        c.privmsg(e.source.nick, "echo: %s" % (e.arguments[0]))
        #c.privmsg(self.channel, "delma on spy!")

    def on_pubmsg(self, c, e):
        #a = e.arguments[0].split(":", 1)
        #if len(a) > 1 and strings.lower(a[0]) == strings.lower(self.connection.get_nickname()):
        #   self.do_command(e, a[1].strip())
        msg = e.arguments[0]
        if msg[0] == '!':
            cmd = msg[1:]
            self.do_command(e, cmd)
        if self.connection.get_nickname() in msg:
            c.privmsg(self.channel, "%s, you talkin' to me?" % (e.source.nick))

    def on_dccmsg(self, c, e):
        pass

    def on_dccchat(self, c, e):
        pass

    def add_to_topic(self, connection):
        for name, obj in self.channels.items():
            c.privmsg(self.channel, obj.topic)

    def say_hi(self, connection, event):
        human = Person.get_person(event)
        human.talk_to(connection, "hello!")

    def start_game(self):
        self.say_to_all(self.connection, 'Let the games begin! I will give each of you your roles in private')
        for human in self.participants:
            human.talk_to(self.connection, 'Guess what? You\'re a spy!')

    def end_game(self):
        winner = 'resistance' # game.winner or sth
        self.game_in_progress = False
        self.say_to_all(self.connection, 'The %s has won!' % (winner))
        self.participants = []

    def join_game(self, c, e):
        # TODO check if there is room in current game
        # TODO check if player is alrdy in game
        human = Person.get_person(e)
        if self.game_in_progress:
            human.talk_to(c, 'The game is in progress, cannot join')
        else:
            self.participants.add(human)
            self.say_to_all(c, 'You are in the game. When ready command !start')

    def list_participants(self):
        if not self.participants:
            self.connection.privmsg(self.channel, "There are no participants")
        else:
            players = ', '.join(map(lambda p:p.nick, self.participants))
            self.connection.privmsg(self.channel, players)


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

    def talk_to(self, connection, message):
        connection.privmsg(self.nick, message)

