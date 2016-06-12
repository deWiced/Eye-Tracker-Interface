
import numpy as np
from sklearn.ensemble import RandomForestClassifier


class ActionLearner:
    def __init__(self, data):
        self.original_data = data
        self.model = self.learn(data[:, :-1], data[:, -1])

    def learn(self, data_x, data_y):
        clf = RandomForestClassifier()
        clf = clf.fit(data_x, data_y)
        return clf

    def predict(self, features):
        features = features.reshape(1, -1)
        prediction = self.model.predict(features)[0]  # test this
        prediction_probs = self.model.predict_proba(features)[0]
        prediction_prob = max(prediction_probs)
        print prediction, prediction_probs, prediction_prob

        return prediction, prediction_prob


if __name__ == '__main__':
    # TODO: normalize data?
    test_data = np.array([[0, 0, 0, "a"], [0.2, 0.2, 0.2, "b"], [0.4, 0.4, 0.4, "c"], [0.6, 0.6, 0.5,"d"], [0.8, 0.8, 0.8, "e"], [1, 1, 1, "f"]]) #[0.1, 0.1, 0.1, 0],
    learner = ActionLearner(test_data, 0.5)
    learner.predict(np.array([0.5, 0.5, 0.5]))


