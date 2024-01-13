import os

import pandas as pd
from luigi import LocalTarget, Parameter, Task

from .load_data import TrainTestSplit
from .preprocess_heart import preprocess

SHARED_RELATIVE_PATH = "data"


class PreProcessing(Task):
    """  Preprocesses given data. Data is given by data parameter.
    train_or_test parameter determines which part (train or test) of the data will be preprocessed.
    Preprocessed data will be saved to local data folder.
    """

    data = Parameter(default="heart.csv")
    train_or_test = Parameter(default="train")

    def requires(self):
        return TrainTestSplit(self.data, self.train_or_test)

    def output(self):
        path = os.path.join(
            os.path.abspath(SHARED_RELATIVE_PATH),
            "preprocessed_" + self.train_or_test + ".csv",
        )
        return LocalTarget(path)

    def run(self):
        df = pd.read_csv(self.input().path)
        df_preprocessed = preprocess(df, self.train_or_test)
        df_preprocessed.to_csv(self.output().path, index=False)
