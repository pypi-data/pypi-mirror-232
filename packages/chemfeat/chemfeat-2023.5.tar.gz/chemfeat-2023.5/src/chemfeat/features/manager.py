#!/usr/bin/env python3

'''
Manage feature calculations.
'''

import contextlib
import hashlib
import logging
import multiprocessing
import pathlib

from rdkit import Chem
from simple_file_lock import FileLock
import pandas as pd


from chemfeat.database import FeatureDatabase
from chemfeat.features.calculator import FEATURE_CALCULATORS, PREFIX_SEPARATOR
from chemfeat.modules import import_modules


LOGGER = logging.getLogger(__name__)
NAME_KEY = 'name'
INCHI_COLUMN = FeatureDatabase.INCHI_COLUMN_NAME


def import_calculators(paths=None):
    '''
    Import the feature calculator subclasses.

    Args:
        paths:
            An optional list of paths to external modules with feature
            calculator subclasses. The register method of each FeatureCalculator
            subclass should be called by the module after the subclass is
            defined to register the feature calculator globally.

            File paths will import single modules while directory paths will
            recursively import all modules contained in the directory.

    Returns:
        A dict mapping feature set names to feature calculator subclasses.
    '''
    search_paths = [
        pathlib.Path(__file__).resolve().parent / 'calculators'
    ]
    if paths:
        search_paths.extend(paths)

    import_modules(
        search_paths,
        path_log_msg='Feature calculator search path: %s'
    )
    return FEATURE_CALCULATORS.copy()


def _calculate_features(inchi_and_feat_calcs):
    '''
    Internal function for calculating features with a multiprocessing pool.

    Args:
        inchi_and_feat_calcs:
            A 2-tuple consisting of an InChi string and a list of feature
            calculators.

    Returns:
        The InChi and the dict of features.
    '''
    inchi, feat_calcs = inchi_and_feat_calcs
    features = {}
    LOGGER.debug('Converting %s to molecule', inchi)
    molecule = Chem.inchi.MolFromInchi(inchi)
    if molecule is None:
        LOGGER.error('Failed to convert InChi to molecule object: %s', inchi)
        return None, features
    for calc in feat_calcs:
        # TODO
        # If there is a problem using the same FeatureCalculator objects with
        # multiprocessing, instantiate new objects using the class and
        # parameters.
        calc.add_features(features, molecule)
    return inchi, features


class FeatureManager():
    '''
    Calculate features from InChis and save the results to a database.
    '''
    def __init__(self, feature_database, features):
        '''
        Args:
            feature_database:
                A FeatureDatabase object.

            features:
                An iterable of dicts. Each dict must contain the key "name"
                which designates the feature set to use. All other key-value
                pairs in the dict will be interpretted as parameters for the
                designated feature set.

        Raises:
            See parse().
        '''
        self.feature_database = feature_database
        self.parse(features)
        self.inchis = None
        self.molecules = None

    def parse(self, features):
        '''
        Parse feature specifications.

        Args:
            features:
                Same as __init__().

        Raises:
            ValueError:
                A required key was absent or invalid.
        '''
        all_feat_calcs = import_calculators()
        feat_calcs = {}
        for parameters in features:
            try:
                name = parameters.pop(NAME_KEY)
            except KeyError as err:
                raise ValueError('Feature specification lacks "name" key.') from err
            try:
                calc_cls = all_feat_calcs[name]
            except KeyError as err:
                raise ValueError(f'Unrecognized feature set: {name}') from err
            calc = calc_cls(**parameters)
            feat_calcs[calc.identifier] = calc
        self.feature_calculators = feat_calcs

    def get_feature_parameters(self):
        '''
        Get the feature parameters from the currently configured features.

        Returns:
            A list of features as accepted by __init__().

        '''
        for calc in self.feature_calculators.values():
            params = calc.parameters
            params[NAME_KEY] = calc.FEATURE_SET_NAME
            yield params

    def is_numeric(self, feature_name):
        '''
        Check if a feature is numeric as opposed to categorical.

        Args:
            feature_name:
                The name of the feature.

        Returns:
            True if the feature is numeric, False if it is categorical.
        '''
        set_name, name = feature_name.split(PREFIX_SEPARATOR, 1)
        return self.feature_calculators[set_name].is_numeric(name)

    def numeric_mask(self, feature_names):
        '''
        Get a mask for the numeric features.

        Args:
            feature_names:
                An iterable of feature names.

        Returns:
            A Pandas series of booleans that serve as a mask.
        '''
        if not isinstance(feature_names, pd.Series):
            feature_names = pd.Series(feature_names)
        return feature_names.apply(self.is_numeric)

    def categoric_mask(self, feature_names):
        '''
        Get a mask for categoric features. This is just a wrapper around
        numeric_mask() that accepts the same arguments and inverts the mask.
        '''
        return ~self.numeric_mask(feature_names)

    @property
    def feature_set_string(self):
        '''
        A unique string representing the feature set.
        '''
        long_identifier = ' '.join(calc.identifier for calc in self.feature_calculators.values())
        return hashlib.sha256(long_identifier.encode('utf-8')).hexdigest()

    def filter_feature_specs(self, inchis):
        '''
        Filter feature specifications based on what is already in the database.
        This assumes that the existing database tables contain the expected
        data, which may not be the case if the feature sets have changed.

        Args:
            inchis:
                An iterable of target InChis.

        Returns:
            A filtered list of 2-tuples mapping InChis to the missing feature
            specifications.
        '''
        precalculated = []
        for calc in self.feature_calculators.values():
            existing_inchis = set(self.feature_database.inchis_in_table(calc.identifier))
            precalculated.append((existing_inchis, calc))

        for inchi in inchis:
            feat_calcs = []
            for existing_inchis, calc in precalculated:
                if inchi not in existing_inchis:
                    feat_calcs.append(calc)
            # Only yield the InChi if there are uncalculated features.
            if feat_calcs:
                yield inchi, feat_calcs

    def calculate_features(
        self,
        inchis,
        output_path=None,
        return_dataframe=False,
        n_jobs=-1
    ):
        '''
        Get the path to a CSV file with the current feature set. If the file
        does not exist, it will be created.

        Args:
            inchis:
                An iterable of InChi strings.

            output_path:
                An optional output path for saving the results to a CSV file.

            return_dataframe:
                If True, return a Pandas dataframe with the results.

            n_jobs:
                The number of jobs to use when calculating features.
        '''
        if output_path:
            output_path = pathlib.Path(output_path).resolve()
            output_ctxt = FileLock(output_path)
        else:
            output_ctxt = contextlib.nullcontext(output_path)

        with FileLock(self.feature_database.path), output_ctxt:
            if n_jobs < 1:
                n_jobs = multiprocessing.cpu_count()

            with multiprocessing.Pool(n_jobs) as pool:
                # Convert to a list to avoid passing generator with SQlite
                # database reference to threads/processes, which raises an
                # exception.
                features = pool.imap_unordered(
                    _calculate_features,
                    list(self.filter_feature_specs(inchis))
                )

                features = (
                    (inchi, feats)
                    for inchi, feats in features
                    if inchi is not None and feats
                )
                self.feature_database.insert_features(features)

            feature_set_names = [calc.identifier for calc in self.feature_calculators.values()]
            if output_path:
                self.feature_database.save_csv(output_path, feature_set_names, inchis=inchis)
            if return_dataframe:
                return self.feature_database.get_dataframe(feature_set_names, inchis=inchis)
        return None
