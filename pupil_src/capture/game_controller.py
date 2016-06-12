'''
Game controller stuff that is really fancy and all that jazz.
It's also a plugin. Mind = blown. But not like Jesse was.
'''

from plugin import Plugin
from subprocess import Popen, PIPE
from scipy import stats
import numpy as np
import sys
import threading
from action_learner import ActionLearner


class Action:
    action_count = 11

    IDLE, W, E, N, S, SW, SE, NW, NE, SPECIAL_0, SPECIAL_1 = range(action_count)

    def to_string(self, action):
        if action == self.IDLE:
            return "Idle "  # test this
        elif action == self.W:
            return "Left "
        elif action == self.E:
            return "Right "
        elif action == self.N:
            return "Up "
        elif action == self.S:
            return "Down "
        elif action == self.SW:
            return ["Down ", "Left "]
        elif action == self.SE:
            return ["Down ", "Right "]
        elif action == self.NW:
            return ["Up ", "Left "]
        elif action == self.NE:
            return ["Up ", "Right "]
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

    def __init__(self, g_pool, filter_active=True, simulate_keypresses=True, no_action_radius=0.25):
        super(GameController, self).__init__(g_pool)
        self.filter_active = filter_active
        self.simulate_keypresses = simulate_keypresses
        self.no_action_radius = no_action_radius
        self.gaze_history = []
        self.action_history = [Action.IDLE]  # redundant?
        self.action = Action.IDLE

        self.pause = True
        self.calibrated = True  # TODO: FALSE! in kalibracija!
        self.learned = False

        self.calibrator = None

        self.click_count = 0
        self.learning_repetitions = 3
        self.learning_index = 0
        self.learning_data = []
        self.learning_data_single_take = []
        self.accepted_threshold = 0.5
        self.learner = None

        # fake test
        x = np.arange(100)
        y = np.random.rand(100)
        self.fake_gaze_history = [((x[i],y[i]),1) for i in range(len(x))]
        #self.fake_gaze_history = [((0,0),1), ((1/2,1/2),1)]
        self.fake_action_history = [Action.SW, Action.IDLE]
        self.fake_frame_hold = 60
        self.fake_counter = 0

        #threading.Thread(target=self.key_capturing).start()

    def update(self, frame, events):
        # TODO: last 3? so there are more per frame???

        frame_positions = []

        if self.filter_active:
            for pt in events.get('gaze_positions', []):
                frame_positions.append((self.filter.filter(pt['norm_pos'], pt['timestamp']), pt['confidence']))
        else:
            for pt in events.get('gaze_positions', []):
                frame_positions.append((pt['norm_pos'], pt['confidence']))

        if self.calibrated:
            pass  # frame_positions = self.calibrator.transform(frame_positions)

        self.gaze_history += frame_positions
        self.gaze_history[:-100] = []  # max gaze history length

        if self.pause:
            return

        # calibrate
        if not self.calibrated and len(self.gaze_history) == 100:
            # TODO: calibrate in pol vsakic skos to fuknes tocke za naprej obdelat
            # fuknes v calibrator cel history
            # self.calibrator = Calibrator(self.gaze_history) # kle nardi instanco v kero pol zgori
            # sam filas shit
            # self.calibrated = True
            pass

        if not self.learned and self.click_count % 2 == 1:
            self.learning_data_single_take += frame_positions

        if not self.learned and len(self.learning_data) == self.learning_repetitions * Action.action_count:
            self.learner = ActionLearner(self.learning_data, self.accepted_threshold)
            self.learned = True

        if self.calibrated and self.learned:
            self.update_action()

    def on_click(self, pos, button, action):
        if self.click_count > self.learning_repetitions * Action.action_count * 2:
            return

        # !!! press down, do the action, release !!!
        actions = [Action.IDLE, Action.W, Action.E, Action.N, Action.S,
                   Action.SW, Action.SE, Action.NW, Action.NE,
                   Action.SPECIAL_0, Action.SPECIAL_1]

        self.click_count += 1

        if self.click_count % 2 == 0:
            print self.learning_data_single_take + [actions[self.learning_index]]
            self.learning_data.append(self.learning_data_single_take + [actions[self.learning_index]])
            self.learning_data_single_take = []

            if self.click_count % (2 * self.learning_repetitions) == 0:
                self.learning_index += 1

        # 1. click = start collecting calibration data
        # 2. click = stop and calibrate

        # 3. click = start collecting learning data - N
        # 4. click = stop

        # 5. click = start collecting learning data - S
        # 6. click = stop

        # 7. click = start collecting learning data - W
        # 8. click = stop

        # 9. click = start collecting learning data - E
        # 10. click = stop

        # 11. click = start collecting learning data - NW
        # 12. click = stop

        # 13. click = start collecting learning data - NE
        # 14. click = stop

        # 15. click = start collecting learning data - SW
        # 16. click = stop

        # 17. click = start collecting learning data - SE
        # 18. click = stop

        # 19. click = start collecting learning data - V
        # 20. click = stop

        # 21. click = start collecting learning data - A
        # 22. click = stop

        print self.click_count


    def recognize_action(self):
      
        # TODO: check if direction or a special action. If special detected, delete gaze history.
        # TODO: problem je diferenciirat med simple smernimi akcijami in izvajanjem specialnih
        # TODO: ce je smerna NE izbrises historija; ko detektira da se izvaja posebna akcija blocka normalne in
        # TODO: odklene ko faila ali konca specialno?
        # TODO: triggras specialne iz idle pa ne tko da zacne normalne delat.

        #ali je simple akcija
        short_gaze_len = 10

        try:
            short_gaze_history = self.gaze_history[:short_gaze_len]
            
            #min in max vrednost
            min_index = [gaze[0][1] for gaze in self.gaze_history].index(min([gaze[0][1] for gaze in self.gaze_history]))
            min_x, min_y = self.gaze_history[min_index][0]
            max_index = [gaze[0][1] for gaze in self.gaze_history].index(max([gaze[0][1] for gaze in self.gaze_history]))
            max_x, max_y = self.gaze_history[max_index][0]

            #centroid in devianco se racuna na krajsem gaze_history-ju, ker je akcija krajsa
            centroid_x = sum([gaze[0][0] for gaze in short_gaze_history])/short_gaze_len
            centroid_y = sum([gaze[0][1] for gaze in short_gaze_history])/short_gaze_len
            centroid_dev = (sum([(gaze[0][0]-centroid_x)**2+(gaze[0][1]-centroid_y)**2 for gaze in short_gaze_history])/short_gaze_len)**(1/2)

            #special akcije se racuna na celotnem gaze history
            #aproksimiramo s polinomom 2. stopnje
            points = np.array([gaze[0] for gaze in self.gaze_history])

            # get x and y vectors
            x = points[:,0]
            y = points[:,1]

            # calculate polynomial
            z = np.polyfit(x, y, 2, full= True) #Polynomial coefficients, highest power first; residuals; rank; singular values; cond. tresh.
            features = np.append(np.array(z[0]), np.array(z[1]))
            features = np.append(features, np.array([min_x, min_y, max_x, max_y, centroid_x, centroid_y, centroid_dev]))

            self.gaze_history = []

            print(features)

            action_pred = self.ActionLearner.predict(features)

        except:
            print("except")
            action_pred = Action.IDLE

	return action_pred


    def update_action(self):

        # TODO: kle v recognize dej da zracuna znacilke za zadne tok pa tok framov tko da dobis tok
        # znacilk kot je treba pol jih pa fuknes tko v self.learner.predict(features)
        # in ti vrne Action.NEKI
        # vse to kar ti delas more bit v predict metodi ne kle v game controllerju
        # tm pa tko k prdicta dobi vn tut en procent, in ce je ta mansi kot threshold ti na roko dolocs
        # kasna je akcija in jo returnas!!!!!!!!!!!!!!!!!

        # torej: v recognize nared extrakcijo znacilk in posl v prediktor
        # v prediktorju dobis action, ce je pa % pod thresholdom pa na roke dolocs kera akcija je,
        # tko k zdele delas i think v recognize_action

        self.action = self.recognize_action()
        self.action_history.append(self.action)
        self.action_history[:-7] = []

        if self.simulate_keypresses:
            self.update_keypress()

        '''
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
		'''
        


    def update_keypress(self):
        # TODO: only change when different action, otherwise continuous press (game engine)
        if self.action_history[-1] == self.action:
            return

        print self.action
        action = Action()  # TODO: NEMORS KR TKO! ce sta dva pressa mors oba nehat izvajat!

        if self.action_history[-1] == Action.NW or self.action_history[-1] == Action.NE \
                or self.action_history[-1] == Action.SW or self.action_history[-1] == Action.SE:
            self.simulate_keypress("keyup " + action.to_string(self.action_history[-1])[0])
            self.simulate_keypress("keyup " + action.to_string(self.action_history[-1])[1])
        else:
            self.simulate_keypress("keyup " + action.to_string(self.action_history[-1]))

        if self.action == Action.IDLE:
            return
        elif self.action == Action.N:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.S:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.W:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.E:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.SW:
            self.simulate_keypress("keydown " + action.to_string(self.action)[1])  # self.action[0] ??? wat srsly glej faking kodo k pises shit
            self.simulate_keypress("keydown " + "space ")
        elif self.action == Action.SE:
            self.simulate_keypress("keydown " + action.to_string(self.action)[0])
            self.simulate_keypress("keydown " + action.to_string(self.action)[1])
        elif self.action == Action.NW:
            self.simulate_keypress("keydown " + action.to_string(self.action)[0])
            self.simulate_keypress("keydown " + action.to_string(self.action)[1])
        elif self.action == Action.NE:
            self.simulate_keypress("keydown " + action.to_string(self.action)[0])
            self.simulate_keypress("keydown " + action.to_string(self.action)[1])
        elif self.action == Action.SPECIAL_0:
            self.simulate_keypress("keydown " + action.to_string(self.action))
        elif self.action == Action.SPECIAL_1:
            self.simulate_keypress("keydown " + action.to_string(self.action))

    def simulate_keypress(self, sequence):
        p = Popen(['xte'], stdin=PIPE)
        p.communicate(input=sequence)

    '''
    def process(self, key):
        if key == 'p':
            self.pause = not self.pause
        if key == 'c':
            self.calibrated = True
        elif key == 'x':
            exit('exitting')
        #else:
        #    print( key, end="", flush = True)
        print self.calibrated
        sys.stdout.flush()

    def key_capturing(self):
        while True:
            self.process(sys.stdin.read(1))
    '''

if __name__ == '__main__':
    ctrl = GameController([])
