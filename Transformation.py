from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils import check_random_state, check_arrays
from itertools import combinations
from collections import Counter
import numpy as np
from scipy.misc import comb
__all__ = ['Relabel' ,'Interaction']

class Relabel(BaseEstimator, TransformerMixin):
    '''
    relabel the nominal features by integers
    '''
    def __init__(self):
        pass
    def fit(self, X, y=None):
        '''
        X is an array of shape [n_samples, n_features]

        '''
        m, n = X.shape
        self.map_ = []
        for j in xrange(n):
            levels = np.unique(X[:,j])
            n_levels = len(levels)
            labels = 1+np.arange(n_levels)
            self.map_.append(dict([(levels[i],labels[i]) for i in range(n_levels)]))
        return self
    def transform(self, X):
        '''
        new lable 0 means unknown
        '''
        m, n = X.shape
        newX = np.empty((m, n), dtype=int)
        for j in xrange(n):
            for i in xrange(m):
                try:
                    newX[i,j] = self.map_[j][X[i,j]]
                except KeyError:
                    newX[i,j] = 0
        return newX 
    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X)
            
class Interaction(BaseEstimator, TransformerMixin):
    '''
    Get interaction features from nominal features
    '''
    def __init__(self, degree=2, threshold=2):
        self.degree = degree
        self.threshold = threshold
    def fit(self, X, y=None):
        '''
        Parameters
        ----------
        X: dense matrix of shape [n_samples, n_features] and type int
        each column is a nominal feature

        Returns
        -------
        dense matrix of shape [n_samples, nchoosek(n_features, self.degree)]
        '''
        X = check_arrays(X, sparse_format='dense', dtype=np.int)[0]
        m, n = X.shape
        self.map_ = []
        for i, indices in enumerate(combinations(range(n), self.degree)):
            counter = Counter()
            for v in X[:, indices]:
                counter[tuple(v)] += 1
            local_map = {}
            new_label = 1
            for v in counter.keys():
                if counter[v] >= self.threshold:
                    local_map[v] = new_label
                    new_label += 1
            self.map_.append(local_map)
        return self
    def transform(self, X):
        '''
        if new feature is labeled 0, then it is unknown
        '''
        X = check_arrays(X, sparse_format='dense', dtype=np.int)[0]
        m, n = X.shape
        ret = np.empty((m,comb(n, self.degree, exact=1)))
        for j, indices in enumerate(combinations(range(n), self.degree)):
            for i, v in enumerate(X[:, indices]):
                try:
                    ret[i,j] = self.map_[j][tuple(v)]
                except KeyError:
                    ret[i,j] = 0
        return ret
    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X)
