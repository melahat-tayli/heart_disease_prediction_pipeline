import os
import pickle
from functools import wraps

import pandas as pd
from luigi import LocalTarget, Parameter, Task, format
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from .preprocess_data import PreProcessing

SHARED_RELATIVE_PATH = "data"

registered_models_and_scores = {}


def register(func):
    """Decorator to register model name and scores. """

    @wraps(func)
    def wrapped(*args, **kwargs):
        clf, model_name, training_score = func(*args, **kwargs)
        registered_models_and_scores[model_name + "_training_score"] = training_score

        return clf, model_name, training_score

    return wrapped


@register
def fit_model(model, x_train, y_train):
    """Takes a model name and data. Fits the model. Returns trained model, model name and accuracy score on the same data"""
    clf = model()
    clf.fit(x_train, y_train)
    y_train_pred = clf.predict(x_train)
    return clf, model.__name__, accuracy_score(y_train, y_train_pred)


class Train(Task):
    """ Takes data, train_or_test and model as parameters. It is suggested to set train_or_test parameter to "train".
     Saves trained model parameters to output file defined in output method"
    """

    data = Parameter(default="heart.csv")
    train_or_test = Parameter("train")
    model = Parameter(default=RandomForestClassifier)

    def requires(self):
        return PreProcessing(self.data, self.train_or_test)

    def output(self):
        """Returns Local Target"""
        path = os.path.join(
            os.path.abspath(SHARED_RELATIVE_PATH),
            self.model.__name__ + "_parameters" + ".pkl",
        )
        return LocalTarget(path, format=format.Nop)

    def run(self):
        """Calls fit_model method to train the model. Then saves model parameters to output file."""
        df = pd.read_csv(self.input().open("r"))
        x_train = df.drop(columns=["target"])
        y_train = df["target"]
        clf, model_name, acc_score = fit_model(self.model, x_train, y_train)
        with open(self.output().path, "wb") as f:
            pickle.dump(clf, f)
        self.show_registered()

    def show_registered(self):
        """ Model score is shown when running luigi pipeline. Saves registered model scores to shared relative path folder"""
        print("####################")
        print("Registered_models_and_training_scores:", registered_models_and_scores)
        print("####################")
        df_registered_models = pd.DataFrame.from_dict(
            registered_models_and_scores, orient="index"
        )
        df_registered_models.to_csv(
            os.path.join(SHARED_RELATIVE_PATH, self.train_or_test + "scores.csv")
        )
