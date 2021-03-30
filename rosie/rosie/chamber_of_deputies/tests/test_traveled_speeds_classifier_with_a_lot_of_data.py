from unittest import TestCase

import numpy as np
import pandas as pd
from sklearn.externals import joblib
import sklearn
from numpy.testing import assert_array_equal
import logging

from rosie.chamber_of_deputies.classifiers.traveled_speeds_classifier import TraveledSpeedsClassifier


class TestTraveledSpeedsClassifierWithALotOfData(TestCase):

    def setUp(self):
        self.log = logging.getLogger(__name__)
        self.log.info("starting test") # debug
        self.subject = joblib.load('rosie/chamber_of_deputies/tests/fixtures/traveledspeedsclassifier_model.pkl')
        self.log.info("model loaded")
        self.dataset = pd.read_csv('rosie/chamber_of_deputies/tests/fixtures/traveledspeedsclassifier_dataset.csv')
        self.log.info("dataset loaded")

    def test_a_lot_of_data_prediction(self):
        self.log.info(f"test_a_lot_of_data_prediction -> {type(self.subject).__name__}")
        prediction = self.subject.predict(self.dataset)
        self.assertEqual(len(prediction), len(self.dataset))
        self.assertEqual(len(prediction), 4006016)
        self.log.info("test finished")
