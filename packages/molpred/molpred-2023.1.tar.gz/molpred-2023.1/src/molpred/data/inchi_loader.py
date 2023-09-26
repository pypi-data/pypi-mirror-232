#!/usr/bin/env python3

'''
Class for loading CSV files with InChis and associated data.
'''

import logging
import pathlib

import pandas as pd

from molpred.data.column_specifier import ColumnSpecifier


LOGGER = logging.getLogger(__name__)

# The default InChi column name.
INCHI_COLUMN = 'InChi'


class InChiLoader():
    '''
    Convenience class for loading InChis with optional target columns from CSV files.
    '''

    # Map of names to registered functions that can be used as column
    # transformers when loading data. This allows the transformers to be
    # specified using text configuration such as YAML files.
    TRANSFORMERS = {}

    def __init__(
        self,
        path,
        inchi_column=INCHI_COLUMN,
        column_specifier=None,
        transformers=None
    ):
        '''
        Args:
            path:
                The path to the CSV file.

            inchi_column:
                The name of the column containing the InChi strings. Defaults to
                the value of molpred.common.INCHI_COLUMN.

            column_specifier:
                An instance of ColumnSpecifier for specifying feature and target
                columns to load from the data, or a dict of keyword arguments
                that can be used to instantiate an instance of ColumnSpecifier.

            transformers:
                An optional dict mapping column names to functions that should
                be applied to the the values in the column. If functions have
                been registered with InChiLoader.register_transformer then the
                registered name can be use in place of the function. It may also
                be specified as a list of 2-tuples which will be converted to a
                dict.
        '''
        self.path = pathlib.Path(path).resolve()
        self.inchi_column = inchi_column
        if isinstance(column_specifier, dict):
            column_specifier = ColumnSpecifier(**column_specifier)
        self.column_specifier = column_specifier

        LOGGER.debug('InputLoader: loading %s', path)
        columns = sorted(column_specifier.names) if column_specifier else []
        self.data = pd.read_csv(
            path,
            usecols=[self.inchi_column, *columns]
        ).set_index(self.inchi_column)

        if transformers:
            if isinstance(transformers, dict):
                transformers = transformers.items()
            for name, func in transformers:
                if isinstance(func, str):
                    try:
                        func = self.TRANSFORMERS[func]
                    except KeyError as err:
                        raise ValueError(f'"{func} is not a registered function name') from err
                self.data[name] = self.data[name].apply(func)

    @classmethod
    def register_transformer(cls, name, func):
        '''
        Register a transformer function under the given name. The name can then
        be used as a value in the transformers dict passed to __init__.

        Args:
            name:
                The name under which to register the function.

            func:
                A function that accepts a value and returns a value, which can
                be applied to a column of a data frame.
        '''
        cls.TRANSFORMERS[name] = func

    @property
    def mtime(self):
        '''
        The last modification time of the data.
        '''
        return self.path.stat().st_mtime

    @property
    def inchis(self):
        '''
        The InChis in the input data.
        '''
        return self.data.index.to_series(name=self.inchi_column)

    def join(
        self,
        dataframe,
        columns=None,
        inchi_column=None,
    ):
        '''
        Join columns from the loaded data to the given dataframe. This uses an
        inner join on the InChi column.


        Args:
            dataframe:
                The dataframe to which the target columns should be joined. It
                must contain an InChi column.

            columns:
                An iterable of column names to join from the loaded data. If
                None, then all of the loaded columns will be joined.

            inchi_column:
                The name of the passed dataframe's InChi column. If None, the
                name of the loaded data's InChi column will be used.

        Returns:
            The joined dataframe.
        '''
        if inchi_column is None:
            inchi_column = self.inchi_column

        columns = sorted(
            self.column_specifier.names if columns is None else set(columns)
        )

        if columns:
            return dataframe.join(self.data[columns], on=inchi_column, how='inner')
        return dataframe
