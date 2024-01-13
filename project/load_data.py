import os

import pandas as pd
from luigi import ExternalTask, LocalTarget, Parameter, Task, format
from luigi.contrib.s3 import S3Target
from sklearn.model_selection import StratifiedShuffleSplit

EXTERNAL_DATA_ROOT = "s3://csci-e29-2020fa-final-project"  # Root S3 path, as a constant
SHARED_RELATIVE_PATH = "data"  # shared local and external relative path


class UploadRawData(Task):
    """Uploads local data to amazon s3 bucket"""

    data = Parameter(default="heart.csv")  # Filename of the data file as a parameter

    def output(self):
        """Returns S3Target"""
        s3_data_target_path = os.path.join(
            EXTERNAL_DATA_ROOT, SHARED_RELATIVE_PATH, self.data
        )
        return S3Target(s3_data_target_path, format=format.Nop)

    def run(self):
        """ Writes local data to external target"""
        local_data_path = os.path.join(os.path.abspath(SHARED_RELATIVE_PATH), self.data)

        with self.output().open("w") as o:
            with open(local_data_path, "rb") as i:
                o.write(i.read())


class DownloadRawData(Task):
    """Downloads amazon s3 bucket data to local"""

    """In this project local data is needed for bokeh visualization"""

    data = Parameter(default="heart.csv")  # Filename of the data file as a parameter

    def requires(self):
        return RawData(self.data)

    def output(self):
        """Returns S3Target"""
        local_target_path = os.path.join(SHARED_RELATIVE_PATH, self.data)
        return LocalTarget(local_target_path, format=format.Nop)

    def run(self):
        """ Writes external target to local data"""
        with self.output().open("w") as o:
            with self.input().open("r") as i:
                o.write(i.read())


class RawData(ExternalTask):
    """ Returns S3 Target object for location of raw data"""

    data = Parameter(default="heart.csv")  # Filename of the data under the root s3 path

    def output(self):
        # return the S3Target of the raw data
        path = os.path.join(EXTERNAL_DATA_ROOT, SHARED_RELATIVE_PATH, self.data)
        return S3Target(path, format=format.Nop)


class TrainTestSplit(Task):
    """ Splits raw data as train and test, then returns train or test data depending on the train_or_test parameter.
    if train_or_test=train, it returns train data; if train_or_test=test, it returns test data as csv file
    """

    data = Parameter(default="heart.csv")  # Filename of the data file as a parameter

    train_or_test = Parameter(default="train")  # Parameter to get train or test data

    def requires(self):
        return RawData(self.data)

    def output(self):
        path = os.path.join(
            EXTERNAL_DATA_ROOT, SHARED_RELATIVE_PATH, self.train_or_test + ".csv"
        )
        return S3Target(path)

    def run(self):
        df = pd.read_csv(self.input().open("r"))
        sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
        for train_index, test_index in sss.split(df, df["target"]):
            strat_train_set = df.loc[train_index]
            strat_test_set = df.loc[test_index]
        if self.train_or_test == "train":
            strat_train_set.to_csv(self.output().path, index=False)
        if self.train_or_test == "test":
            strat_test_set.to_csv(self.output().path, index=False)
