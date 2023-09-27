import numpy as np
from scipy import sparse
import pandas as pd

def inv(A):
    """Inverse of square pandas DataFrame."""
    if np.isscalar(A): A = pd.DataFrame(np.array([[A]]))

    B = np.linalg.inv(A)
    return pd.DataFrame(B,columns=A.columns,index=A.index)

def matrix_product(X,Y):
    """Compute matrix product X@Y, allowing for possibility of missing data."""

    return X.fillna(0)@Y.fillna(0)

def diag(X):

    try:
        assert X.shape[0] == X.shape[1]
        d = pd.Series(np.diag(X),index=X.index)
    except IndexError: # X is a series?
        # We can wind up blowing ram if not careful...
        d = sparse.diags(X.values)
        d = pd.DataFrame.sparse.from_spmatrix(d,index=X.index,columns=X.index)
    except AttributeError: # Not a pandas object?
        d = np.diag(X)

    return d

def outer(S,T):
    """Outer product of two series (vectors) S & T.
    """
    return pd.DataFrame(np.outer(S,T),index=S.index,columns=T.index)

import numpy as np
import pandas as pd

def qr(X):
    """
    Pandas-friendly QR decomposition.
    """
    assert X.shape[0]>=X.shape[1]

    Q,R = np.linalg.qr(X)
    Q = pd.DataFrame(Q,index=X.index, columns=X.columns)
    R = pd.DataFrame(R,index=X.columns, columns=X.columns)

    return Q,R

def leverage(X):
    """
    Return leverage of observations in X (the diagonals of the hat matrix).
    """

    Q = qr(X)[0]

    return (Q**2).sum(axis=1)

def hat_factory(X):
    """
    Return a function hat(y) that returns X(X'X)^{-1}X'y.

    This is the least squares prediction of y given X.

    We use the fact that  the hat matrix is equal to QQ',
    where Q comes from the QR decomposition of X.
    """
    Q = qr(X)[0]

    def hat(y):
        return Q@(Q.T@y)

    return hat

from statsmodels.stats.correlation_tools import cov_nearest as _cov_nearest
import pandas as pd

def cov_nearest(V,threshold=1e-12):
    """
    Return a positive definite matrix which is "nearest" to the symmetric matrix V,
    with the smallest eigenvalue not less than threshold.
    """
    s,U = np.linalg.eigh((V+V.T)/2) # Eigenvalue decomposition of symmetric matrix

    s = np.maximum(s,threshold)

    return V*0 + U@np.diag(s)@U.T  # Trick preserves attributes of dataframe V

import pandas as pd
import numpy as np

def trim(df,alpha):
    """Trim values below alpha quantile and above (1-alpha) quantile.

    This maps individual extreme elements of df to NaN.
    """
    xmin = df.quantile(alpha)
    xmax = df.quantile(1-alpha)
    return df.where((df>=xmin)*(df<=xmax),np.nan)
