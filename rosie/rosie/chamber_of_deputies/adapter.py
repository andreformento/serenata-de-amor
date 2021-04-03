from rosie.core.log_factory import LogFactory
import os
from datetime import date
from pathlib import Path
from re import match

import numpy as np
import pandas as pd
from urllib.error import HTTPError

from serenata_toolbox.chamber_of_deputies.reimbursements import Reimbursements
from serenata_toolbox.datasets import fetch


class Adapter:

    STARTING_YEAR = 2009
    COMPANIES_DATASET = '2016-09-03-companies.xz'
    REIMBURSEMENTS_PATTERN = r'reimbursements-\d{4}\.csv'
    RENAME_COLUMNS = {
        'subquota_description': 'category',
        'total_net_value': 'net_value',
        'cnpj_cpf': 'recipient_id',
        'supplier': 'recipient'
    }
    DTYPE = {
        'applicant_id': np.str,
        'cnpj_cpf': np.str,
        'congressperson_id': np.str,
        'subquota_number': np.str
    }

    def __init__(self, path, skip_loaded_files=False):
        self.path = path
        self.skip_loaded_files = skip_loaded_files
        self.log = LogFactory(__name__).create()
        current_year = date.today().year # TODO +1 -> 2021 was removed because have a problem -> ValueError: new categories need to have the same number of items as the old categories!
        self.years = range(self.STARTING_YEAR, current_year)

    def __iter__(self):
        self.current_year_index = 0
        return self

    def __next__(self):
        if self.current_year_index < len(self.years):
            year = self.years[self.current_year_index]
            dataset_chunk = self.__get_dataset_chunk_by_year(year)
            self.current_year_index += 1
            return year, dataset_chunk
        else:
            raise StopIteration

    def __get_dataset_chunk_by_year(self, year):
        dataset_chunk = self.read_reimbursements(year=year).merge(
            self.companies,
            how='left',
            left_on='cnpj_cpf',
            right_on='cnpj'
        )
        self.prepare_dataset(dataset_chunk)
        return dataset_chunk

    def load_datasets(self):
        self.load_companies()
        self.load_reimbursements()

    def load_companies(self):
        if self.skip_loaded_files and os.path.isfile(os.path.join(self.path, self.COMPANIES_DATASET)):
            self.log.info(f'Update companies skiped')
        else:
            self.log.info('Updating companies')
            os.makedirs(self.path, exist_ok=True)
            fetch(self.COMPANIES_DATASET, self.path)

    def load_reimbursements(self, year=None):
        if self.skip_loaded_files and self.__get_reimbursements_paths(year=year):
            self.log.info(f'Update reimbursements skiped')
        else:
            for year in self.years:
                self.log.info(f'Updating reimbursements from {year}')
                try:
                    Reimbursements(year, self.path)()
                except HTTPError as e:
                    self.log.error(f'Could not update Reimbursements from year {year}: {e} - {e.filename}')

    @property
    def dataset(self):
        df = self.reimbursements.merge(
            self.companies,
            how='left',
            left_on='cnpj_cpf',
            right_on='cnpj'
        )
        self.prepare_dataset(df)
        self.log.info('Full dataset ready!')
        return df

    @property
    def companies(self):
        self.log.debug('Loading companies')
        path = Path(self.path) / self.COMPANIES_DATASET
        df = pd.read_csv(path, dtype={'cnpj': np.str}, low_memory=False)
        df['cnpj'] = df['cnpj'].str.replace(r'\D', '')
        return df

    @property
    def reimbursements(self):
        return self.read_reimbursements()

    def __get_reimbursements_paths(self, year=None):
        paths = (
            str(path) for path in Path(self.path).glob('*.csv')
            if match(self.REIMBURSEMENTS_PATTERN, path.name)
        )

        return [path for path in paths if (not year) or str(year) in path]

    def read_reimbursements(self, year=None):
        df = pd.DataFrame()
        filtered_paths = self.__get_reimbursements_paths(year=year)

        for path in filtered_paths:
            self.log.debug(f'Loading reimbursements from {path}')
            year_df = pd.read_csv(path, dtype=self.DTYPE, low_memory=False)
            df = df.append(year_df)

        return df

    def prepare_dataset(self, df):
        self.rename_categories(df)
        self.coerce_dates(df)
        self.rename_columns(df)

    def rename_columns(self, df):
        self.log.debug('Renaming columns to Serenata de Amor standard')
        df.rename(columns=self.RENAME_COLUMNS, inplace=True)

    def rename_categories(self, df):
        self.log.debug('Categorizing reimbursements')

        # There's no documented type for `3`, `4` and `5`, thus we assume it's
        # an input error until we hear back from Chamber of Deputies
        types = ('bill_of_sale', 'simple_receipt', 'expense_made_abroad')
        converters = {number: None for number in range(3, 6)}
        df['document_type'].replace(converters, inplace=True)
        df['document_type'] = df['document_type'].astype('category')
        df['document_type'].cat.rename_categories(types, inplace=True)

        # Some classifiers expect a more broad category name for meals
        rename = {'Congressperson meal': 'Meal'}
        df['subquota_description'] = df['subquota_description'].replace(rename)
        df['is_party_expense'] = df['congressperson_id'].isnull()

    def coerce_dates(self, df):
        for field, fmt in (('issue_date', '%Y-%m-%d'), ('situation_date', '%d/%m/%Y')):
            self.log.debug(f'Coercing {field} column to date data type')
            df[field] = pd.to_datetime(df[field], format=fmt, errors='coerce')
