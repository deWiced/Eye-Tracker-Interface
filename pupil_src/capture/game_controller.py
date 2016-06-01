'''
Game controller stuff that is really fancy and all that jazz.
It's also a plugin. Mind = blown. But not like Jesse was.
'''

from plugin import Plugin


class GameController(Plugin):

    def __init__(self, g_pool):
        super(GameController, self).__init__(g_pool)
        self.simulate_keypresses = True

    def simulate_keypress(self):
        pass
