class Calibrator(left, right):
    '''
    Class for calibrating pupil positions, takes left and right margin end extends these proportionally to the lower and upper bound (0,1)
    '''
	var center
	var ratioLeft
	var ratioRight

    def __init__(self, points[]):
	for point in points:
		if point < left
			left = point
		if point > right
			right = point

	center = (self.right + self.left) / 2
	ratioLeft = center/(center - self.left)
	ratioRight = (1.0 - center)/(self.right - center)

    def calibration(newLeft, newRight):
	var calibratedLeft = center - ((center - self.newLeft) * ratioLeft)
	if calibratedLeft < 0.0
		calibratedLeft = 0.0
	var calibratedRight = center + ((self.newRight - center) * ratioRight)
	if calibratedRight > 1
		calibratedRight = 1
