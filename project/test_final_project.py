"""Tests for final project package"""
import os
from unittest import TestCase

from luigi import LocalTarget, build
from luigi.contrib.s3 import S3Target
from sklearn.linear_model import LogisticRegression

from final_project.load_data import (DownloadRawData, RawData, TrainTestSplit,
                                     UploadRawData)
from final_project.preprocess_data import PreProcessing
from final_project.testperformance_model import TestModel, model_performance
from final_project.train import Train, fit_model


class UploadRawDataTests(TestCase):
    def test_output_path(self):
        self.assertEqual(
            UploadRawData().output().path,
            "s3://csci-e29-2020fa-final-project/data/heart.csv",
        )

    def test_output_return(self):
        self.assertEqual(UploadRawData().output().__class__, S3Target)

    def test_params(self):
        self.assertEqual(len(UploadRawData().get_params()), 1)

    def test_run_method(self):
        self.assertTrue(UploadRawData().output().exists())


class DownloadRawDataTests(TestCase):
    def test_output_path(self):
        self.assertEqual(DownloadRawData().output().path, "data/heart.csv")

    def test_output_return(self):
        self.assertEqual(DownloadRawData().output().__class__, LocalTarget)

    def test_params(self):
        self.assertEqual(len(DownloadRawData().get_params()), 1)

    def test_run_method(self):
        build([DownloadRawData()], local_scheduler=True)
        self.assertTrue(DownloadRawData().output().exists())


class RawDataTests(TestCase):
    def test_output_path(self):
        self.assertEqual(
            RawData().output().path, "s3://csci-e29-2020fa-final-project/data/heart.csv"
        )

    def test_output_return(self):
        self.assertEqual(RawData().output().__class__, S3Target)

    def test_params(self):
        self.assertEqual(len(RawData().get_params()), 1)

    def test_run_method(self):
        self.assertTrue(RawData().output().exists())


class TrainTestSplitTests(TestCase):
    def test_output_path(self):
        self.assertEqual(
            TrainTestSplit().output().path,
            "s3://csci-e29-2020fa-final-project/data/train.csv",
        )
        self.assertEqual(
            TrainTestSplit(train_or_test="test").output().path,
            "s3://csci-e29-2020fa-final-project/data/test.csv",
        )

    def test_output_return(self):
        self.assertEqual(TrainTestSplit().output().__class__, S3Target)

    def test_run_method(self):
        self.assertTrue(TrainTestSplit(train_or_test="test").output().exists())
        self.assertTrue(TrainTestSplit().output().exists())

    def test_params(self):
        self.assertEqual(len(TrainTestSplit().get_params()), 2)

    def test_requires(self):
        self.assertEqual(TrainTestSplit().requires(), RawData())


class TrainTests(TestCase):
    def test_output_path(self):
        self.assertEqual(
            Train().output().path,
            os.path.join(os.getcwd(), "data/RandomForestClassifier_parameters.pkl"),
        )

    def test_output_return(self):
        self.assertEqual(Train().output().__class__, LocalTarget)

    def test_params(self):
        self.assertEqual(len(Train().get_params()), 3)

    def test_requires(self):
        self.assertEqual(Train().requires(), PreProcessing())

    def test_fit_model(self):
        clf, model_name, training_score = fit_model(
            LogisticRegression, [[2], [3], [4], [-1], [-2], [-3]], [1, 1, 1, 0, 0, 0]
        )
        self.assertTrue(isinstance(clf, LogisticRegression))
        self.assertEqual(model_name, "LogisticRegression")

    def test_run(self):
        build([Train()], local_scheduler=True)
        self.assertTrue(os.path.isfile(Train().output().path))


class PreProcessingTests(TestCase):
    def test_requires(self):
        self.assertEqual(PreProcessing().requires(), TrainTestSplit())

    def test_params(self):
        self.assertEqual(len(PreProcessing().get_params()), 2)

    def test_output_return(self):
        self.assertEqual(PreProcessing().output().__class__, LocalTarget)

    def test_output_path(self):
        self.assertEqual(
            PreProcessing().output().path,
            os.path.join(os.getcwd(), "data/preprocessed_train.csv"),
        )

    def test_run(self):
        build([PreProcessing()], local_scheduler=True)
        self.assertTrue(os.path.isfile(PreProcessing().output().path))


class TestModelTests(TestCase):
    def test_params(self):
        self.assertEqual(len(TestModel().get_params()), 4)

    def test_output_return(self):
        self.assertEqual(TestModel().output().__class__, LocalTarget)

    def test_output_path(self):
        self.assertEqual(
            TestModel().output().path, os.path.join(os.getcwd(), "data/plotting.png")
        )

    def test_model_performance(self):
        clf, model_name, training_score = fit_model(
            LogisticRegression, [[2], [3], [4], [-1], [-2], [-3]], [1, 1, 1, 0, 0, 0]
        )
        model_name, acc_score = model_performance(
            model_name, clf, [[4], [-1], [7], [-2], [7], [-3]], [1, 0, 1, 0, 1, 0]
        )
        self.assertTrue(0 <= acc_score <= 1)

    def test_run(self):
        build(
            [TestModel(model=LogisticRegression, source_test="test")],
            local_scheduler=True,
        )

        self.assertTrue(os.path.isfile(TestModel().output().path))
