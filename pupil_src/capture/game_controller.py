'''
Game controller stuff that is really fancy and all that jazz.
It's also a plugin. Mind = blown. But not like Jesse was.
'''

from plugin import Plugin
from subprocess import Popen, PIPE
from scipy import stats


class Action:
    IDLE, LEFT, RIGHT, UP, DOWN = range(5)

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

    def __init__(self, g_pool, filter_active=True, simulate_keypresses=True, no_action_radius=0.25):
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

	#ali je simple akcija
	short_gaze_len = 10
	distance_treshold = 0.07
	
	try:
		short_gaze_history = self.gaze_history[:short_gaze_len]

		centroid_x = sum([gaze[0][0] for gaze in short_gaze_history])/short_gaze_len
		centroid_y = sum([gaze[0][1] for gaze in short_gaze_history])/short_gaze_len
		short_gaze_history_dev = (sum([(gaze[0][0]-centroid_x)**2+(gaze[0][1]-centroid_y)**2 for gaze in short_gaze_history])/short_gaze_len)**(1/2)
		if short_gaze_history_dev <= distance_treshold:
			self.gaze_history = []
			if (((centroid_x-1/2)**2+(centroid_y-1/2)**2)**(1/2) <= self.no_action_radius):
				return Action.IDLE
			elif (centroid_y>2/3):
				if (centroid_x >2/3):
					##tuki bi rabla dve akciji, se UP
					return Action.RIGHT
				elif (centroid_x > 1/3):
					return Action.UP
				else:
					##tud tuki se UP
					return Action.LEFT
			elif (centroid_y > 1/3):
				if (centroid_x>1/2):
					return Action.RIGHT
				else:
					return Action.LEFT
			else:
				if (centroid_x >2/3):
					##tuki bi rabla dve akciji, se DOWN
					return Action.RIGHT
				elif (centroid_x > 1/3):
					return Action.UP
				else:
					##tud tuki se DOWN
					return Action.LEFT
		else:
			##check if special action
			middle_index = len(self.gaze_history)//2
			slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(self.gaze_history[:middle_index][0])
			slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(self.gaze_history[middle_index:][0])
			if (abs(slope1+slope2)<0.2 and slope1*slope2<0):
				if (slope1<0):
					self.gaze_history = []
					return Action.V
				elif (slope2<0):
					self.gaze_history = []
					return Action.A
				else:
					return Action.IDLE
			else:
				return Action.IDLE
	except:
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
