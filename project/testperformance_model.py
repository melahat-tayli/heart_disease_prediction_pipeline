import os
import pickle
from functools import wraps

import pandas as pd
from luigi import LocalTarget, Parameter, Task, format
from sklearn.ensemble import RandomForestClassifier

from .preprocess_data import PreProcessing
from .train import Train

SHARED_RELATIVE_PATH = "data"

registered_models_and_scores = {}


def register(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        model_name, testing_score = func(*args, **kwargs)
        registered_models_and_scores[model_name + "_testing_score"] = testing_score
        return model_name, testing_score

    return wrapped


@register
def model_performance(model_name, loaded_model, x_test, y_test):
    acc_score = loaded_model.score(x_test, y_test)
    return model_name, acc_score


class TestModel(Task):
    """ Takes data, source_train, source_test and model as parameters. It is suggested to set source_train parameter to "train" and source_test parameter to 'test'.
    Plots test scores to a Local Target output file (defined in output method.)
    """

    data = Parameter(default="heart.csv")
    source_train = Parameter(default="train")
    model = Parameter(default=RandomForestClassifier)
    source_test = Parameter(default="test")

    def requires(self):
        return {
            "model_param": Train(self.data, self.source_train, self.model),
            "test_data": PreProcessing(self.data, self.source_test),
        }

    def output(self):
        path = os.path.join(os.path.abspath(SHARED_RELATIVE_PATH), "plotting" + ".png")
        return LocalTarget(path, format=format.Nop)

    def run(self):
        """Loads trained model and tests model performance on pretrained test data. Plots model scores and saves it in the output file."""
        loaded_model = pickle.load(open(self.input()["model_param"].path, "rb"))
        df_test = pd.read_csv(self.input()["test_data"].path)
        x_test = df_test.drop(columns=["target"])
        y_test = df_test["target"]
        model_name = os.path.splitext(
            os.path.basename(self.input()["model_param"].path)
        )[0]
        model_performance(model_name, loaded_model, x_test, y_test)
        df_registered_models = pd.DataFrame.from_dict(
            registered_models_and_scores, orient="index"
        )
        plot = df_registered_models.plot.bar(
            title="Model scores on Test data set", legend=False
        )
        plot.set_xlabel("Model Names")
        plot.set_ylabel("Model scores")
        fig = plot.get_figure()
        fig.savefig(self.output().path, bbox_inches="tight", dpi=100)
        self.show_registered()

    def show_registered(self):
        """ Model score is shown when running luigi pipeline. Saves registered model scores to shared relative path folder"""
        print("***********************")
        print("Registered_models_and_training_scores:", registered_models_and_scores)
        print("***********************")
        df_registered_models = pd.DataFrame.from_dict(
            registered_models_and_scores, orient="index",
        )
        df_registered_models.to_csv(
            os.path.join(SHARED_RELATIVE_PATH, self.source_test + "scores.csv")
        )
