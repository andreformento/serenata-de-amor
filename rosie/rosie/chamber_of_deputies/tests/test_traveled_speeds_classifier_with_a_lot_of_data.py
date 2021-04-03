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

    def read_chunk(self, df_chunk):
        self.log.info(f"dataset loaded")
        self.log.info(f"df_chunk type -> {type(df_chunk)}")
        self.log.info(df_chunk)
        df_chunk.info()
        prediction = self.subject.predict(df_chunk)
        # self.assertEqual(len(prediction), len(df_chunk))
        # self.assertEqual(len(prediction), 4006016)
        self.log.info(f"test finished {len(df_chunk)}/{len(prediction)}")
        return prediction

    def test_a_lot_of_data_prediction(self):
        self.log.info(f"test_a_lot_of_data_prediction -> {type(self.subject).__name__}")

        chunk_size = 100
        batch_no = 0
        filename = 'rosie/chamber_of_deputies/tests/fixtures/traveledspeedsclassifier_dataset.csv'

        for df_chunk in pd.read_csv(filename,chunksize=chunk_size,iterator=True):
            # df_chunk.to_sql('chunk_sql',csv_database, if_exists='append')
            prediction_chunk = self.read_chunk(df_chunk)
            self.log.info(f"prediction_chunk type -> {type(prediction_chunk)}")
            batch_no+=1
            print('index: {}'.format(batch_no))

        # for chunk in pd.read_csv('rosie/chamber_of_deputies/tests/fixtures/traveledspeedsclassifier_dataset.csv', chunksize=chunk_size):
        # with pd.read_csv(filename, chunksize=chunk_size) as reader:
        #     for df_chunk in reader:
        #         # self.dataset = pd.read_csv('rosie/chamber_of_deputies/tests/fixtures/traveledspeedsclassifier_dataset.csv')
        #         self.log.info(f"{i}: dataset loaded")
        #         self.log.info(df_chunk)
        #         prediction = self.subject.predict(df_chunk)
        #         # self.assertEqual(len(prediction), len(df_chunk))
        #         # self.assertEqual(len(prediction), 4006016)
        #         self.log.info(f"{i}: test finished {len(df_chunk)}/{len(prediction)}")
        #         i = i + 1
