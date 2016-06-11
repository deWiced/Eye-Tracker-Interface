'''
Game controller stuff that is really fancy and all that jazz.
It's also a plugin. Mind = blown. But not like Jesse was.
'''

from plugin import Plugin
from subprocess import Popen, PIPE


class Action:
    IDLE, LEFT, RIGHT, UP, DOWN, SPECIAL_0, SPECIAL_1 = range(7)

    def to_string(self, action):
        if action == self.IDLE:
            return "Idle "  # test this
        elif action == self.LEFT:
            return "Left "
        elif action == self.RIGHT:
            return "Right "
        elif action == self.UP:
            return "Up "
        elif action == self.DOWN:
            return "Down "
        elif action == self.SPECIAL_0:
            return "Escape "
        elif action == self.SPECIAL_1:
            return "N "


class Smoothing_Filter(object):
    def __init__(self):
        super(Smoothing_Filter, self).__init__()
        self.prev = None
        self.prev_ts = None
        self.smoother = 0.5
        self.cut_dist = 0.01

    def filter(self,vals,ts):
        self.prev = vals
        self.pref_ts = ts
        self.filter = self._filter
        return vals

    def _filter(self,vals,ts):
        result = []
        for v,ov in zip(vals,self.prev):
            if abs(ov-v)>self.cut_dist:
                self.prev = tuple(vals)
                return vals
            else:
                result.append(ov+self.smoother*(v-ov))
        self.prev = result
        return type(vals)(result)


class GameController(Plugin):
    '''
    Central area where nothing happens, and 4 directions where shit happens.
    '''
    # TODO: keypress start/stop when over radius threshold (game engine type checking).

    def __init__(self, g_pool, filter_active=True, simulate_keypresses=True, no_action_radius=0.5):
        super(GameController, self).__init__(g_pool)
        self.filter_active = filter_active
        self.simulate_keypresses = simulate_keypresses
        self.no_action_radius = no_action_radius
        self.gaze_history = []
        self.action_history = [Action.IDLE]  # redundant?
        self.action = Action.IDLE

        # fake test
        self.fake_gaze_history = [((-1,0), 1), ((0,0), 1), ((1,0), 1), ((0,0), 1)]
        self.fake_action_history = [Action.LEFT, Action.IDLE, Action.RIGHT, Action.IDLE]
        self.fake_frame_hold = 60
        self.fake_counter = 0


    def update(self, frame, events):
        # TODO: last 3? so there are more per frame???

        if self.filter_active:
            for pt in events.get('gaze_positions', []):
                self.gaze_history.append((self.filter.filter(pt['norm_pos'], pt['timestamp']), pt['confidence']))
        else:
            for pt in events.get('gaze_positions', []):
                self.gaze_history.append((pt['norm_pos'], pt['confidence']))

        self.gaze_history[:-100] = []  # max gaze history length
        #print self.gaze_history

        self.update_action()


    def recognize_action(self):
        # TODO: check if direction or a special action. If special detected, delete gaze history.
        # TODO: problem je diferenciirat med simple smernimi akcijami in izvajanjem specialnih
        # TODO: ce je smerna NE izbrises historija; ko detektira da se izvaja posebna akcija blocka normalne in
        # TODO: odklene ko faila ali konca specialno?
        # TODO: triggras specialne iz idle pa ne tko da zacne normalne delat.
        return Action.IDLE


    def update_action(self):
        # TODO: from gaze to action

        self.action = self.recognize_action()
        self.action_history.append(self.action)
        self.action_history[:-7] = []

        if self.simulate_keypresses:
            self.update_keypress()

        # fake test
        if not self.fake_frame_hold:
            self.action = self.fake_action_history[self.fake_counter % len(self.fake_action_history)]

            # TODO: not here
            if self.simulate_keypresses:
                self.update_keypress()
            self.action_history.append(self.action)
            self.action_history[:-3] = []

            self.fake_counter += 1
            self.fake_frame_hold = 60
        else:
            self.fake_frame_hold -= 1



    def update_keypress(self):
        # TODO: only change when different action, otherwise continuous press (game engine)
        if self.action_history[-1] == self.action:
            return

        print self.action

        action = Action()
        self.simulate_keypress("keyup " + action.to_string(self.action_history[-1]))

        if self.action == Action.IDLE:
            return
        elif self.action == Action.UP:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.DOWN:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.LEFT:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.RIGHT:
            self.simulate_keypress("keydown " + action.to_string(self.action))


    def simulate_keypress(self, sequence):
        p = Popen(['xte'], stdin=PIPE)
        p.communicate(input=sequence)
