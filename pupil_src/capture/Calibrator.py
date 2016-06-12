class Calibrator:
    """
    Class for calibrating pupil positions, takes left and right margin end extends these proportionally to the lower and upper bound (0,1)
    Vsakic ko se dobi nove tocke, je treba preverit ce je tocka na levi strani ali desni od centra in potem jo pomnozit s ta pravim ratioLeftX oz RatioRightX
    """
    def __init__(self, gaze_history):
        left = 1
        right = 0.001
        x = [gaze[0][0] for gaze in gaze_history]
        y = [gaze[0][1] for gaze in gaze_history]

        for point in x:
            if point < left:
                left = point
            if point > right:
                right = point

        self.centerX = (right + left) / 2
        self.ratioLeftX = self.centerX/(self.centerX - left)
        self.ratioRightX = (1.0 - self.centerX)/(right - self.centerX)

        left = 1
        right = 0.001
        for point in y:
            if point < left:
                left = point
            if point > right:
                right = point

        self.centerY = (right + left) / 2
        self.ratioLeftY = self.centerY/(self.centerY - left)
        self.ratioRightY = (1.0 - self.centerY)/(right - self.centerY)

    def transform(self, new_gaze):
        """calibration transformation started, first we need to find if the X and Y are on the left or right side of the new center defined in the init method"""
        calibratedLeftX = 10
        calibratedRightX = -10
        calibratedLeftY = 10
        calibratedRightY = -10
        calibratedPoints = []
        """then we need to check if the alpha factor is not too big and the new points are out the interval 0-1"""

        if new_gaze[0][0] < self.centerX:
            newleftX = new_gaze[0][0]
            calibratedLeftX = self.centerX - ((self.centerX - newleftX) * self.ratioLeftX)
 	    if calibratedLeftX < 0.1:
                calibratedLeftX = 0.1
            calibratedPoints.append(calibratedLeftX)
        else:
            newrightX = new_gaze[0][0]
            calibratedRightX = self.centerX + ((newrightX - self.centerX) * self.ratioRightX)
	    if calibratedRightX > 1:
                calibratedRightX = 1
            calibratedPoints.append(calibratedRightX)
        if new_gaze[0][1] < self.centerY:
            newleftY = new_gaze[0][1]
            calibratedLeftY = self.centerY - ((self.centerY - newleftY) * self.ratioLeftY)
	    if calibratedLeftY < 0.1:
                calibratedLeftY = 0.1
            calibratedPoints.append(calibratedLeftY)
        else:
            newrightY = new_gaze[0][1]
            calibratedRightY = self.centerY + ((newrightY - self.centerY) * self.ratioRightY)
            if calibratedRightY > 1:
                calibratedRightY = 1
            calibratedPoints.append(calibratedRightY)
	"""print calibratedPoints"""
        return calibratedPoints

if __name__ == '__main__':
	test_gaze_history = [((0.2,0.4),1),((0.4,0.2),1),((0.4,0.4),1),((0.2,0.2),1)]
	CalibratorTest = Calibrator(test_gaze_history)
	CalibratorTest.transform([(0.2,0.2)])
	CalibratorTest.transform([(0.4,0.4)])
	CalibratorTest.transform([(0.3,0.3)])
