class Calibrator(left, right):
    '''
    Class for calibrating pupil positions, takes left and right margin end extends these proportionally to the lower and upper bound (0,1)
    '''
	var center
	var ratioLeft
	var ratioRight

    def __init__(self, left, right):
	
	center = (self.right + self.left) / 2
	ratioLeft = center/(center - self.left)
	ratioRight = (1.0 - center)/(self.right - center)

    def calibration(newLeft, newRight):
 
	var calibratedLeft = center - ((center - self.newLeft) * ratioLeft)
	var calibratedRight = center + ((self.newRight - center) * ratioRight)
