from irc import bot
from irc import strings

class DefianceBot(bot.SingleServerIRCBot):
    
    def __init__(self, channel, nick, server, port, **params):
        super(DefianceBot, self).__init__([(server, port)], nick, 'github.com/PolarPayne/DefianceBot', reconnection_interval=60, **params)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + '_')

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and strings.lower(a[0]) == strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())

    def on_dccmsg(self, c, e):
        pass

    def on_dccchat(self, c, e):
        pass

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        else:
            c.notice(nick, "Not understood: " + cmd)


