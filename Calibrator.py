class Calibrator():
	'''
	Class for calibrating pupil positions, takes left and right margin end extends these proportionally to the lower and upper bound (0,1)
	'''
	def setParam(self, points):
		left = 1
		right = 0.001
		for point in points:
			if point < left:
				left = point
			if point > right:
				right = point

		self.center = (right + left) / 2
		self.ratioLeft = self.center/(self.center - left)
		self.ratioRight = (1.0 - self.center)/(right - self.center)

	def calibration(self, newLeft, newRight):
		calibratedLeft = self.center - ((self.center - self.newLeft) * self.ratioLeft)
		if calibratedLeft < 0.1:
			calibratedLeft = 0.1
		calibratedRight = self.center + ((self.newRight - self.center) * self.ratioRight)
		if calibratedRight > 1:
			calibratedRight = 1
