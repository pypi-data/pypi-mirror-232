#!/usr/bin/env python3

'''
Convenience class for working with feature and target columns.
'''


def _as_set(items):
    '''
    Convert an iterable to a set.

    Args:
        items:
            An iterable or None.

    Returns:
        The set of the input items. If None then an empty set it returned.
    '''
    return set(items) if items is not None else set()


class ColumnSpecifier():
    '''
    Specify numeric and categoric feature and target column names.
    '''
    def __init__(self, num_feats=None, cat_feats=None, num_targets=None, cat_targets=None):
        '''
        Args:
            num_feats:
                An iterable of numeric feature names.

            cat_feats:
                An iterable of categoric feature names.

            num_targets:
                An iterable of numeric target names.

            cat_targets:
                An iterable of categoric target names.
        '''
        self.num_feats = _as_set(num_feats)
        self.cat_feats = _as_set(cat_feats)
        self.num_targets = _as_set(num_targets)
        self.cat_targets = _as_set(cat_targets)

    @property
    def numeric_names(self):
        '''
        The set of all numeric names.
        '''
        return self.num_feats | self.num_targets

    @property
    def categoric_names(self):
        '''
        The set of all categoric names.
        '''
        return self.cat_feats | self.cat_targets

    @property
    def features(self):
        '''
        The set of feature names.
        '''
        return self.num_feats | self.cat_feats

    @property
    def targets(self):
        '''
        The set of target names.
        '''
        return self.num_targets | self.cat_targets

    @property
    def names(self):
        '''
        The set of all feature and target names.
        '''
        return self.features | self.targets

    def is_numeric(self, name):
        '''
        True if the given name is one of the numeric features or targets.
        '''
        return name in self.numeric_names

    def is_categoric(self, name):
        '''
        True if the name is one of the categoric features or targets.
        '''
        return name in self.categoric_names

    def is_feature(self, name):
        '''
        True if the name is a feature.
        '''
        return name in self.features

    def is_target(self, name):
        '''
        True if the name is a target.
        '''
        return name in self.targets
