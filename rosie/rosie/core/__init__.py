from rosie.core.log_factory import LogFactory
import os.path

import numpy as np
import pandas as pd
from sklearn.externals import joblib

class Core:
    """
    This is Rosie's core object: it implements a generic pipeline to collect
    data, clean and normalize it. After analyzing the data it outputs a dataset
    with suspicions information. Its initialization module takes a settings
    module and an adapter.

    The settings module should have three constants:
    * CLASSIFIERS (dict) with pairs of human readable name (snake case) for
    each classifier and the object (class) of the classifiers.
    * UNIQUE_IDS (str or iterable) with the column(s) that should be taken as
    unique identifiers if the main dataset of each module.
    * VALUE (str) with the column that should be taken as the total net value
    of the transaction represented by each row of the dataset.

    The adapter should be an object with:
    * A `dataset` property with the main dataset to be analyzed;
    * A `path` property with the path to the datasets (where the output will be
    saved).
    """

    def __init__(self, settings, adapter):
        self.log = LogFactory(__name__).create()
        self.settings = settings
        self.adapter = adapter
        self.data_path = adapter.path

    def __call__(self):
        self.adapter.load_datasets()

        total = len(self.settings.CLASSIFIERS)
        dataset_iter = iter(self.adapter)
        suspicions_by_year = []

        for year, df_chunk in dataset_iter:
            running = 1

            suspicions = df_chunk[self.settings.UNIQUE_IDS].copy() if self.settings.UNIQUE_IDS else df_chunk.copy()

            for name, classifier in self.settings.CLASSIFIERS.items():
                self.log.info(f'{year} :: Running classifier {running} of {total}: {name}')
                model = self.load_trained_model(classifier)
                predicted_chunk_df = self.predict(df_chunk, model, name)

                suspicions[name] = predicted_chunk_df
                if predicted_chunk_df.dtype == np.int:
                    suspicions.loc[predicted_chunk_df == 1, name] = False
                    suspicions.loc[predicted_chunk_df == -1, name] = True

                running += 1

            suspicions_by_year.append(suspicions)

        all_suspicions_years = pd.concat(suspicions_by_year)
        output = os.path.join(self.data_path, f'suspicions.xz')
        kwargs = dict(compression='xz', encoding='utf-8', index=False)
        all_suspicions_years.to_csv(output, **kwargs)

    def load_trained_model(self, classifier):
        model_filename = '{}.pkl'.format(classifier.__name__.lower())
        model_path = os.path.join(self.data_path, model_filename)

        # palliative: this outputs a model too large for joblib
        if classifier.__name__ == 'MonthlySubquotaLimitClassifier':
            full_dataset = self.adapter.dataset
            model = classifier()
            model.fit(full_dataset)
        else:
            if os.path.isfile(model_path):
                model = joblib.load(model_path)
            else:
                full_dataset = self.adapter.dataset
                model = classifier()
                model.fit(full_dataset)
                joblib.dump(model, model_path)
        return model

    def predict(self, df_chunk, model, name):
        model.transform(df_chunk)
        return  model.predict(df_chunk)
