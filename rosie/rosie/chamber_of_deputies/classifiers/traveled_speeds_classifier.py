from itertools import combinations

import numpy as np
import pandas as pd
import logging
from sklearn.base import TransformerMixin
from sklearn.utils.validation import check_is_fitted

from geopy.distance import vincenty as distance


class TraveledSpeedsClassifier(TransformerMixin):
    """
    Traveled Speeds classifier.

    Dataset
    -------
    applicant_id : category column
        A personal identifier code for every person making expenses.

    category : category column
        Category of the expense. The model will be applied just in rows where
        the value is equal to "Meal".

    is_party_expense : bool column
        If the row corresponds to a party expense or not. The model will be
        applied just in rows where the value is equal to `False`.

    issue_date : datetime column
        Date when the expense was made.

    latitude : float column
        Latitude of the place where the expense was made.

    longitude : float column
        Longitude of the place where the expense was made.
    """

    AGG_KEYS = ['applicant_id', 'issue_date']
    COLS = ['applicant_id',
            'category',
            'is_party_expense',
            'issue_date',
            'latitude',
            'longitude']

    def __init__(self, contamination=.001):
        self.log = logging.getLogger(__name__)

        if contamination in [0, 1]:
            raise ValueError('contamination must be greater than 0 and less than 1')

        self.contamination = contamination

    def fit(self, X):
        # self.log.info('fit started') # debug
        _X = self.__aggregate_dataset(X)
        self.polynomial = np.polyfit(_X['expenses'].astype(np.long),
                                     _X['distance_traveled'].astype(np.long),
                                     3)
        self._polynomial_fn = np.poly1d(self.polynomial)
        # self.log.info('fit done') # debug
        return self

    def transform(self, X=None):
        pass

    def predict(self, X):
        # self.log.info('predict started') # debug
        check_is_fitted(self, ['polynomial', '_polynomial_fn'])

        _X = X[self.COLS].copy()
        _X = self.__aggregate_dataset(_X)
        _X = self.__classify_dataset(_X)
        # self.log.info('predict merge started') # debug
        _X = pd.merge(X, _X, how='left', left_on=self.AGG_KEYS, right_on=self.AGG_KEYS)
        # self.log.info('predict merge done') # debug
        is_outlier = self.__applicable_rows(_X) & \
            (_X['expenses_threshold_outlier'] | _X['traveled_speed_outlier'])
        y = is_outlier.astype(np.int).replace({1: -1, 0: 1})
        # self.log.info('predict done') # debug
        return y

    def __aggregate_dataset(self, X):
        # self.log.info('__aggregate_dataset started') # debug
        X = X[self.__applicable_rows(X)]
        # self.log.info('__aggregate_dataset X __applicable_rows done') # debug
        distances_traveled = X.groupby(self.AGG_KEYS) \
            .apply(self.__calculate_sum_distances).reset_index() \
            .rename(columns={0: 'distance_traveled'})
        # self.log.info('groupby distances_traveled done') # debug
        expenses = X.groupby(self.AGG_KEYS)['applicant_id'].agg(len) \
            .rename('expenses').reset_index()
        # self.log.info('groupby expenses done') # debug
        _X = pd.merge(distances_traveled, expenses,
                      left_on=self.AGG_KEYS,
                      right_on=self.AGG_KEYS)
        # self.log.info('__aggregate_dataset done') # debug
        return _X

    def __classify_dataset(self, X):
        # self.log.info('__classify_dataset started') # debug
        X['expected_distance'] = self._polynomial_fn(X['expenses'])
        X['diff_distance'] = abs(X['expected_distance'] - X['distance_traveled'])
        X['expenses_threshold_outlier'] = X['expenses'] > 8
        threshold = self.__threshold_for_contamination(X, self.contamination)
        X['traveled_speed_outlier'] = X['diff_distance'] > threshold
        # self.log.info('__classify_dataset done') # debug
        return X

    def __applicable_rows(self, X):
        self.log.info('__applicable_rows started # break memory') # debug
        result = (X['category'] == 'Meal') & \
            (-73.992222 < X['longitude']) & (X['longitude'] < -34.7916667) & \
            (-33.742222 < X['latitude']) & (X['latitude'] < 5.2722222) & \
            ~X['is_party_expense'] & \
            X[['latitude', 'longitude']].notnull().all(axis=1)
        self.log.info('__applicable_rows done # break memory') # debug
        return result

    def __calculate_sum_distances(self, X):
        coordinate_list = X[['latitude', 'longitude']].values
        edges = list(combinations(coordinate_list, 2))
        result = np.sum([distance(edge[0][1:], edge[1][1:]).km for edge in edges])
        return result

    def __threshold_for_contamination(self, X, expected_contamination):
        # self.log.info('__threshold_for_contamination started') # debug
        possible_thresholds = range(1, int(X['expected_distance'].max()), 50)
        results = [(self.__contamination(X, t), t) for t in possible_thresholds]
        best_choice = min(results, key=lambda x: abs(x[0] - expected_contamination))
        # self.log.info('__threshold_for_contamination done') # debug
        return best_choice[1]

    def __contamination(self, X, threshold):
        return (X['diff_distance'] > threshold).sum() / \
            (len(X) - X['expenses_threshold_outlier'].sum())
