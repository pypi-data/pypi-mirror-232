#!/usr/bin/env python
# [[file:../Empirics/regression.org::*Outer product of two series][Outer product of two series:1]]
# Tangled on Tue Sep 26 10:57:34 2023
import numpy as np
import pandas as pd

def outer(a,b):
    """
    Outer product of two series.
    """

    if type(a) is pd.DataFrame:
        a = a.squeeze()

    if type(b) is pd.DataFrame:
        b = b.squeeze()

    a = pd.Series(a)
    b = pd.Series(b)

    x = np.outer(a,b)

    try:
        x = pd.DataFrame(x,index=a.index,columns=b.index)
    except AttributeError:
        x = pd.DataFrame(x)

    return x
# Outer product of two series:1 ends here

# [[file:../Empirics/regression.org::*Inner product][Inner product:1]]
# Tangled on Tue Sep 26 10:57:34 2023
def to_series(df):
    """
    Stack a dataframe to make a series.
    """
    try:
        df.columns.names = [n if n is not None else "_%d" % i for i,n in enumerate(df.columns.names)]
    except AttributeError: # Already a series?
        return pd.Series(df)

    for n in df.columns.names:
        df = df.stack(n)

    return df

def inner(a,b,idxout,colsout,fill_value=None,method='sum'):
    """
    Compute inner product of sorts, summing over indices of products which don't appear in idxout or colsout.
    """

    a = to_series(a)
    b = to_series(b)

    if fill_value is not None:
        a = a.astype(pd.SparseDtype(fill_value=fill_value))
        b = b.astype(pd.SparseDtype(fill_value=fill_value))

    idxint = list(set(a.index.names).intersection(b.index.names))
    aonly = list(set(a.index.names).difference(idxint))
    bonly = list(set(b.index.names).difference(idxint))

    if fill_value is None: # Non-sparse
        a = a.replace(0.,np.nan).dropna()
        b = b.replace(0.,np.nan).dropna()

    c = pd.merge(a.reset_index(aonly),b.reset_index(bonly),on=idxint)
    c = c.reset_index().set_index(idxint + aonly + bonly)

    sumover = list(set(aonly+bonly+idxint).difference(idxout+colsout))
    keep = list(set(aonly+bonly+idxint).difference(sumover))

    if fill_value is not None:
        foo = c.sparse.to_coo().tocsr()

        foo = foo[:,0].multiply(foo[:,1])
        foo = pd.DataFrame.sparse.from_spmatrix(foo,index=c.index)
    else:
        foo = c.iloc[:,0]*c.iloc[:,1]

    if method=='sum':
        p = foo.groupby(keep).sum()
    elif method=='mean':
        p = foo.groupby(keep).mean()
    else:
        raise ValueError("No method %s." % method)

    p = p.unstack(colsout)

    if len(idxout)>1:
        p = p.reorder_levels(idxout)

    p = p.sort_index()

    if len(colsout):
        p = p.sort_index(axis=1)

    return p
# Inner product:1 ends here

# [[file:../Empirics/regression.org::*SVD with missing data][SVD with missing data:1]]
# Tangled on Tue Sep 26 10:57:34 2023
import pandas as pd
import numpy as np

def svd_missing(X,gls=False):
    """
    Compute rank one approximation to X.
    """
    def ols(y,x,N=None):

        use = y.index.droplevel(['i','t','m'])

        if N is not None:
            N = N[use]
            x = x[use]*N
            y = y*N

        x = pd.DataFrame(x[use])

        b = np.linalg.lstsq(x,y,rcond=None)[0].squeeze()

        return b

    Sigma = X.cov(ddof=0)
    N = X.count()/X.count().sum()

    s2,u = np.linalg.eigh(Sigma)
    b = pd.Series(u[:,-1]*np.sqrt(s2[-1]),index=Sigma.index)

    y = X.stack().dropna()

    if gls:
        v = y.groupby(['i','t','m']).apply(lambda y,x=b: ols(y,x,N))
    else:
        v = y.groupby(['i','t','m']).apply(lambda y,x=b: ols(y,x))

    scale = np.sqrt(v.T@v)
    u = pd.Series(u[:,-1],index=b.index)

    return u,np.sqrt(s2[-1])*scale,v/scale
# SVD with missing data:1 ends here

# [[file:../Empirics/regression.org::*Angle between vectors (or series)][Angle between vectors (or series):1]]
# Tangled on Tue Sep 26 10:57:34 2023
"""
Compute angle between two vectors, thx to https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python/13849249#13849249
"""
import numpy as np

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
# Angle between vectors (or series):1 ends here

# [[file:../Empirics/regression.org::*OLS][OLS:1]]
# Tangled on Tue Sep 26 10:57:34 2023
def ols(y,x):
    try:
        xcols = x.columns
    except AttributeError:
        xcols = x
        x = y[xcols]
        y = y[y.columns.difference(xcols)]

    y,x = drop_missing([y,x])

    b = np.linalg.lstsq(x,y,rcond=None)[0]

    return pd.Series(b.squeeze(),index=x.columns)
# OLS:1 ends here

# [[file:../Empirics/regression.org::*Inter-quartile range][Inter-quartile range:1]]
# Tangled on Tue Sep 26 10:57:34 2023
def iqr(x,std=False):
    y = np.diff(x.quantile([0.25,0.75]))[0]

    # Ratio between std deviation and iqr for normal distribution
    if std: y = y*1.3489795

    return y
# Inter-quartile range:1 ends here

# [[file:../Empirics/regression.org::code:Mp][code:Mp]]
# Tangled on Tue Sep 26 10:57:34 2023
import pandas as pd
import numpy as np
from warnings import warn

def Mp(X):
    """
    Construct X-E(X|p) = (I-S(S'S)^{-1}S')X.

    Drop any categorical variables where taking means isn't sensible.
    """
    if len(X.shape) > 1:
        X = X.loc[:,X.dtypes != 'category']
    else:
        if X.dtype == 'category': warn('Taking mean of categorical variable.')

    use = list(set(['t','m','j']).intersection(X.index.names))

    if len(use):
        return X - X.groupby(use).transform(np.mean)
    else:
        return X - X.mean()
# code:Mp ends here

# [[file:../Empirics/regression.org::code:Mpi][code:Mpi]]
# Tangled on Tue Sep 26 10:57:34 2023

def Mpi(X):
    """
    Construct X-E(X|pi).

    Drop any categorical variables where taking means isn't sensible.
    """
    if len(X.shape) > 1:
        X = X.loc[:,X.dtypes != 'category']
    else:
        if X.dtype == 'category': warn('Taking mean of categorical variable.')

    return X - X.groupby(['t','m']).transform(np.mean)
# code:Mpi ends here

# [[file:../Empirics/regression.org::code:kmeans][code:kmeans]]
# Tangled on Tue Sep 26 10:57:34 2023
from sklearn.model_selection import GroupKFold
from .df_utils import use_indices, drop_missing
from scipy.optimize import minimize_scalar
from sklearn.cluster import KMeans

def kmean_controls(n_clusters,Mpy,Mpd,shuffles=0,classifiers=None,verbose=False):
    n_clusters = int(n_clusters)
    Mpd = Mpd.copy()

    km = KMeans(n_clusters=n_clusters,init='k-means++',n_init=10*int(np.ceil(np.sqrt(n_clusters))))
    tau = km.fit_predict(Mpd)

    if classifiers is not None:
        c = classifiers.values.T.tolist()
        Mpd['tau'] = list(zip(*c,tau))
    else:
        Mpd['tau'] = tau

    Mpd['tau'] = Mpd['tau'].astype('category')

    Mpyg = pd.DataFrame(Mpy).join(Mpd['tau'],how='left').groupby(['t','m','tau'])

    MdMpy = Mp(pd.DataFrame(Mpy) - Mpyg.transform(np.mean)).squeeze()

    # Compare real groups with shuffled groups
    if shuffles:
        Valt = []
        for s in range(shuffles):
            Mpd_alt = Mpd.copy()
            Mpd_alt['tau'] = Mpd['tau'].sample(frac=1).reset_index(drop=True).values

            Mpyg_alt = pd.DataFrame(Mpy).join(Mpd_alt['tau'],how='left').groupby(['tau'])

            Valt.append((pd.DataFrame(Mpy) - Mpyg_alt.transform(np.mean)).squeeze().var())

        lr = 2*(np.log(np.mean(Valt)) - np.log(MdMpy.var()))

        if verbose:
            print('K=%d\tLR=%f\tCoeff of variation=%f' % (n_clusters,lr,np.std(Valt)/np.mean(Valt)))

        return lr,MdMpy
    else:
        return Mpd['tau'],MdMpy


# Construct Md operator which goes with k-means clusters tau.
def Md_generator(X,tau,method='categorical',Mp=False):
    """
    Md operator, for either categorical or linear expectations.
    """

    if method=='categorical': # assuming conditioning is on groups tau
        if 'j' in X.index.names:
            if Mp:
                Xg = pd.DataFrame({'X':X}).join(tau,how='left').groupby(['tau','j','t','m'])
            else:
                Xg = pd.DataFrame({'X':X}).join(tau,how='left').groupby(['tau','j'])
        else:
            if Mp:
                Xg = pd.DataFrame({'X':X}).join(tau,how='left').groupby(['tau','t','m'])
            else:
                Xg = pd.DataFrame({'X':X}).join(tau,how='left').groupby(['tau'])

        MdX = X - Xg.transform(np.mean).squeeze()
    elif method=='linear':
        try:
            taucols = tau.columns
            X = pd.DataFrame(X).join(tau,how='outer')
        except AttributeError:  # tau a Series
            taucols = tau

        if 'j' in X.index.names:
            MdX = X.groupby('j').apply(lambda y,x=taucols: Md_generator(y.droplevel('j'),x,method='linear',Mp=Mp)).T
            try:
                MdX = MdX.stack()
            except AttributeError:
                pass

            MdX = MdX.reorder_levels(['i','t','m','j']).sort_index()
        else:
            # Difference out kmeans if tau provided
            ycols = X.columns.difference(taucols)
            xcols = taucols
            if 'tau' in tau and Mp: # kmeans categories provided
                xcols = taucols.drop('tau')
                group = ['tau']
                if Mp:
                    X = X - X.groupby(['tau','t','m']).transform(np.mean)
                else:
                    X = X - X.groupby(['tau']).transform(np.mean)
            else:
                if Mp:
                    X = X - X.groupby(['t','m']).transform(np.mean)
                else:
                    X = X - X.mean()

            y = X[ycols]
            x = X[xcols]
            y,x = drop_missing([y,x])
            x['Constant'] = 1
            b = np.linalg.lstsq(x,y,rcond=None)[0]
            MdX = pd.Series(y.squeeze() - (x@b).squeeze(),index=y.index)
    else: raise ValueError("No method %s." % method)

    return MdX
# code:kmeans ends here

# [[file:../Empirics/regression.org::*Compute $\MdMpy$][Compute $\MdMpy$:1]]
# Tangled on Tue Sep 26 10:57:34 2023
def estimate_MdMpy(y,d,K=None):

    if K is not None:
        d,MdMpy = kmean_controls(K,Mp(y),Mp(d),classifiers=d.loc[:,d.dtypes == 'category'])
        MdMp = lambda x: Md_generator(x,d,Mp=True)
        Md = lambda x: Md_generator(x,d,Mp=False)
        method = 'categorical'
    else:
        method = 'linear'

        # Change categorical vars to numeric
        cats = d.select_dtypes(['category']).columns
        if len(cats):
            d[cats] = d[cats].apply(lambda x: x.cat.codes)

        MdMp = lambda x: Md_generator(x,d,method=method,Mp=True)
        Md = lambda x: Md_generator(x,d,method=method,Mp=False)

        MdMpy = MdMp(y)

    assert MdMpy.index.names == ['i','t','m','j']

    if not np.all(np.abs(MdMpy.groupby(['j','t','m']).mean()) < 1e-6):
        warn('MdMpy means greater than 1e-6')

    return MdMpy,Md,MdMp,d
# Compute $\MdMpy$:1 ends here

# [[file:../Empirics/regression.org::code:beta_from_MdMpy][code:beta_from_MdMpy]]
# Tangled on Tue Sep 26 10:57:34 2023
from .estimation import svd_missing
import numpy as np

def estimate_beta(MdMpy,
                  heteroskedastic=False,
                  cov = lambda X : pd.DataFrame.cov(X,ddof=0),
                  return_se=False,bootstrap_tol=None,Mdp=None,verbose=False):

    if verbose:
        print("estimate_beta")

    if Mdp:
        MdMpy = Mdp(MdMpy)
    try:
        MdMpY = MdMpy.unstack('j')
    except KeyError:
        MdMpY = MdMpy

    C = cov(MdMpY)

    if np.any(np.isnan(C)):
        raise ValueError(f"Can't compute covariance matrix; too few {C.count().idxmin()}.")

    # Estimate beta
    u,s,vt = svd_missing(C,max_rank=1,heteroskedastic=heteroskedastic)

    if np.sign(u).mean()<0: # Fix sign of u.
        u = -u

    b = pd.DataFrame(u*s,index=MdMpY.columns,columns=['beta'])

    if return_se and bootstrap_tol:
        if bootstrap_tol is None:
            raise ValueError("Not implemented. Specify bootstrap_tol>0.")
            V = (((e-e.mean())**2).mul(v**2,axis=0)).mean() # See p. 150 of Bai (2003)
            seb = np.sqrt(V)
        else:
            its = 0
            B = pd.DataFrame(index=b.index)
            seb=0
            while its < 30 or np.linalg.norm(seb-last) > bootstrap_tol:
                last = seb
                okay = False
                while not okay:
                    try:
                        B[its] = estimate_beta(MdMpY.groupby(['t','m']).sample(frac=1,replace=True))[0]
                        okay = True
                    except ValueError as msg:
                        print(msg)
                seb = B.apply(lambda x:iqr(x,std=True),axis=1)
                if verbose: print(f"On iteration {its} standard error is {seb}.")
                its += 1
            V = B.T.cov()
    else:
        seb = None

    if return_se:
        return b,seb,V
    else:
        return b,None,None
# code:beta_from_MdMpy ends here

# [[file:../Empirics/regression.org::*Estimation of $\M{p}w$][Estimation of $\M{p}w$:1]]
# Tangled on Tue Sep 26 10:57:34 2023
from scipy import sparse
import warnings

def estimate_Mpw(y,b,MdMpy,return_se=False,bootstrap_tol=None,
                 verbose=False):

    # Construct regression to compute Mpw
    cols = y.groupby(['i','t','m']).mean().index

    # This is VERY SLOW.  Find a better way!
    index = pd.MultiIndex.from_tuples([(i[0],i[1],i[2],j) for i in cols.tolist() for j in b.index.tolist()])

    B = sparse.kron(sparse.eye(len(cols)),b,format='csr')
    B = pd.DataFrame.sparse.from_spmatrix(B,index=index,columns=cols)
    B.index.names = ['i','t','m','j']

    # This is VERY, VERY SLOW!  Find a better way!
    #B = B.loc[y.index,:]
    # Reindexing faster, but is not fast.
    B = B.reindex(y.index,axis=0)  #Maybe?

    N = y.index.levels[y.index.names.index('i')]

    TM = [(np.nan,t,m) for t in y.index.levels[y.index.names.index('t')] for m in y.index.levels[y.index.names.index('m')]]

    ITM = [(i,t,m) for i in N for t in y.index.levels[y.index.names.index('t')] for m in y.index.levels[y.index.names.index('m')]]

    R = sparse.kron(np.ones((1,len(N))),sparse.eye(len(TM)),format='csr')
    R = pd.DataFrame.sparse.from_spmatrix(R,index=TM,columns=ITM)
    #R = R.loc[:,cols]
    R = R.reindex(cols,axis=1)

    Zeros = pd.DataFrame(np.zeros((len(TM),len(TM))),index=TM,columns=TM)

    # Matrix multiplication too expensive for pd.DataFrame.sparse...
    B = B.sparse.to_coo()
    BB = B.T@B
    BBdf = pd.DataFrame.sparse.from_spmatrix(BB,index=cols,columns=cols)

    zig = pd.concat([BBdf,R.T],axis=1)
    zag = pd.concat([R,Zeros],axis=1)

    zag.index = pd.MultiIndex.from_tuples(zag.index)
    zag.columns = pd.MultiIndex.from_tuples(zag.columns)

    X0 = pd.concat([zig,
                    zag],axis=0)

    y0 = pd.concat([pd.Series(B.T@MdMpy,index=cols),pd.Series(np.zeros(len(TM)),index=TM)],axis=0)

    X0 = X0.sparse.to_coo().tocsc()

    result = sparse.linalg.lsqr(X0,y0,calc_var=False,atol=1e-16,btol=1e-16)

    coeffs = result[0].squeeze()

    Mpw = pd.Series(coeffs[:len(cols)],index=cols)
    if verbose: print("Estimated Mpw")

    scale = Mpw.std(ddof=0)
    Mpw = Mpw/scale

    mults = pd.Series(coeffs[len(cols):],
                      index=pd.MultiIndex.from_tuples([tm[1:] for tm in TM],names=['t','m']),name='mult')

    if return_se:
        with warnings.catch_warnings():
            warnings.simplefilter('error')
                # X0inv = sparse.linalg.inv(X0)  # Too expensive!
            # se = np.sqrt(sparse.csr_matrix.diagonal(X0inv))

            # Use partioned matrix inverse to get just se of b
            BB = BB*(scale**2)
            # Note that BB is diagonal
            R = R.sparse.to_coo()
            n = B.shape[1]
            m = R.shape[0]
            Ainv = sparse.spdiags(1/BB.diagonal(),0,n,n)
            V22 = sparse.spdiags(1/(R@Ainv@R.T).diagonal(),0,m,m)
            V11 = Ainv - Ainv@R.T@V22@R@Ainv

            se = np.sqrt(V11.diagonal())

            if 'j' in Mpw.index.names:
                Mpw = Mpw[MdMpy.index]

            e1 = (MdMpy - B@Mpw)
            sigma2 = e1.var(ddof=0)

            mults_se = np.sqrt(V22.diagonal())*sigma2

            seb = pd.Series(se[:len(b)]*sigma2,index=b.index)
            mults_se = pd.Series(mults_se,
                                index=pd.MultiIndex.from_tuples([tm[1:] for tm in TM],
                                                                names=['t','m']),
                                name='mults_se')

            return Mpw, scale, mults, seb, mults_se, e1

    return Mpw,scale,mults
# Estimation of $\M{p}w$:1 ends here

# [[file:../Empirics/regression.org::*Estimate Lagrange Multipliers][Estimate Lagrange Multipliers:1]]
# Tangled on Tue Sep 26 10:57:34 2023
def estimate_stderrs(y,scale):

    cols = y.groupby(['i','t','m']).mean().index

    TM = [(np.nan,t,m) for t in y.index.levels[y.index.names.index('t')] for m in y.index.levels[y.index.names.index('m')]]

    with warnings.catch_warnings():
        warnings.simplefilter('error')
            # X0inv = sparse.linalg.inv(X0)  # Too expensive!
        # se = np.sqrt(sparse.csr_matrix.diagonal(X0inv))

        # Use partioned matrix inverse to get just se of b
        BB = BB*(scale**2)
        # Note that BB is diagonal
        R = R.sparse.to_coo()
        n = B.shape[1]
        m = R.shape[0]
        Ainv = sparse.spdiags(1/BB.diagonal(),0,n,n)
        V22 = sparse.spdiags(1/(R@Ainv@R.T).diagonal(),0,m,m)
        V11 = Ainv - Ainv@R.T@V22@R@Ainv

        se = np.sqrt(V11.diagonal())

        if 'j' in Mpw.index.names:
            Mpw = Mpw[MdMpy.index]

        e1 = (MdMpy - B@Mpw)
        sigma2 = e1.var(ddof=0)

        mults_se = np.sqrt(V22.diagonal())*sigma2

        seb = pd.Series(se[:len(b)]*sigma2,index=b.index)
        mults_se = pd.Series(mults_se,
                            index=pd.MultiIndex.from_tuples([tm[1:] for tm in TM],
                                                            names=['t','m']),
                            name='mults_se')


    return seb, mults_se, e1
# Estimate Lagrange Multipliers:1 ends here

# [[file:../Empirics/regression.org::*Estimation of \beta and $\M{p}w$][Estimation of \beta and $\M{p}w$:1]]
# Tangled on Tue Sep 26 10:57:34 2023
from scipy import sparse
import warnings

def estimate_beta_and_Mpw(y,Mdp,return_se=False,bootstrap_tol=None,
                          verbose=False):

    MdMpy = Mdp(y)
    try:
        MdMpY = MdMpy.unstack('j')
    except KeyError:
        MdMpY = MdMpy

    if not np.allclose(MdMpy.groupby(['t','m','j']).mean(),0):
        warn("MdMpy means not close to zero.")

    b,seb,V = estimate_beta(MdMpy,return_se=return_se,bootstrap_tol=bootstrap_tol,verbose=verbose)

    # Construct regression to compute Mpw
    cols = y.groupby(['i','t','m']).mean().index

    # This is VERY SLOW.  Find a better way!
    index = pd.MultiIndex.from_tuples([(i[0],i[1],i[2],j) for i in cols.tolist() for j in b.index.tolist()])

    B = sparse.kron(sparse.eye(len(cols)),b,format='csr')
    B = pd.DataFrame.sparse.from_spmatrix(B,index=index,columns=cols)
    B.index.names = ['i','t','m','j']

    # This is VERY, VERY SLOW!  Find a better way!
    #B = B.loc[y.index,:]
    # Reindexing is not fast.
    B = B.reindex(y.index,axis=0)  #Maybe?

    N = y.index.levels[y.index.names.index('i')]

    TM = [(np.nan,t,m) for t in y.index.levels[y.index.names.index('t')] for m in y.index.levels[y.index.names.index('m')]]

    ITM = [(i,t,m) for i in N for t in y.index.levels[y.index.names.index('t')] for m in y.index.levels[y.index.names.index('m')]]

    R = sparse.kron(np.ones((1,len(N))),sparse.eye(len(TM)),format='csr')
    R = pd.DataFrame.sparse.from_spmatrix(R,index=TM,columns=ITM)
    #R = R.loc[:,cols]
    R = R.reindex(cols,axis=1)

    Zeros = pd.DataFrame(np.zeros((len(TM),len(TM))),index=TM,columns=TM)

    # Matrix multiplication too expensive for pd.DataFrame.sparse...
    B = B.sparse.to_coo()
    BB = B.T@B
    BBdf = pd.DataFrame.sparse.from_spmatrix(BB,index=cols,columns=cols)

    zig = pd.concat([BBdf,R.T],axis=1)
    zag = pd.concat([R,Zeros],axis=1)

    zag.index = pd.MultiIndex.from_tuples(zag.index)
    zag.columns = pd.MultiIndex.from_tuples(zag.columns)

    X0 = pd.concat([zig,
                    zag],axis=0)

    y0 = pd.concat([pd.Series(B.T@MdMpy,index=cols),pd.Series(np.zeros(len(TM)),index=TM)],axis=0)

    X0 = X0.sparse.to_coo().tocsc()

    result = sparse.linalg.lsqr(X0,y0,calc_var=False,atol=1e-16,btol=1e-16)

    coeffs = result[0].squeeze()

    Mpw = pd.Series(coeffs[:len(cols)],index=cols)
    if verbose: print("Estimated Mpw")

    scale = Mpw.std(ddof=0)
    Mpw = Mpw/scale
    b = (b*scale).squeeze()

    mults = pd.Series(coeffs[len(cols):],
                      index=pd.MultiIndex.from_tuples([tm[1:] for tm in TM],names=['t','m']),name='mult')

    if return_se and bootstrap_tol is None: # See Greene-Seaks (1991)
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            # X0inv = sparse.linalg.inv(X0)  # Too expensive!
            # se = np.sqrt(sparse.csr_matrix.diagonal(X0inv))

            # Use partioned matrix inverse to get just se of b
            BB = BB*(scale**2)
            # Note that BB is diagonal
            R = R.sparse.to_coo()
            n = B.shape[1]
            m = R.shape[0]
            Ainv = sparse.spdiags(1/BB.diagonal(),0,n,n)
            V22 = sparse.spdiags(1/(R@Ainv@R.T).diagonal(),0,m,m)
            V11 = Ainv - Ainv@R.T@V22@R@Ainv

            se = np.sqrt(V11.diagonal())

            if 'j' in Mpw.index.names:
                Mpw = Mpw[MdMpy.index]

            e1 = (MdMpy - B@Mpw)
            sigma2 = e1.var(ddof=0)

            mults_se = np.sqrt(V22.diagonal())*sigma2

            seb = pd.Series(se[:len(b)]*sigma2,index=b.index)
            mults_se = pd.Series(mults_se,
                                index=pd.MultiIndex.from_tuples([tm[1:] for tm in TM],
                                                                names=['t','m']),
                                name='mults_se')
    else:
        mults_se = None
        e1 = None

    return b,Mpw,seb,mults,mults_se,e1
# Estimation of \beta and $\M{p}w$:1 ends here

# [[file:../Empirics/regression.org::code:gamma][code:gamma]]
# Tangled on Tue Sep 26 10:57:34 2023
def estimate_gamma(y,beta,w,tau,method='categorical',verbose=False):
    """
    Estimate $gamma(tau) = E[Mp(Y -hat{beta}hat{w}) | tau]$.
    """
    if beta is not None:
        e = y.unstack('j') - pd.DataFrame({0:w})@pd.DataFrame({0:beta}).T
    else:
        e = y.unstack('j')

    if method=='categorical':
        gamma = Mp(e).join(tau,how='left').groupby('tau').mean()
        gamma.columns.name = 'j'

        # Construct gamma(d)
        gamma_d = pd.DataFrame(tau).join(gamma,on='tau')
        gamma_d.columns.name = 'j'
        gamma_d = gamma_d.drop('tau',axis=1)
        gamma_d = gamma_d.stack()
        gamma_d.name = 'gamma_d'

        e = e.stack('j')
    elif method=='linear':
        e = e.stack('j')
        tau['Constant'] = 1

        foo = pd.DataFrame(e).join(tau,how='outer')

        gamma = foo.groupby('j').apply(lambda y,x=tau.columns: ols(y.droplevel('j'),x))
        if gamma.columns.name is None:
            gamma.columns.name = 'k'

        try:
            gamma_d = (tau*gamma).sum(axis=1).dropna()
        except ValueError:
            gamma_d = (tau@gamma.T).stack()

        gamma_d.name = 'gamma_d'
    else: raise ValueError("No method %s." % method)

    #e2 = e - gamma_d.loc[e.index]
    e2 = e - gamma_d.reindex_like(e)

    return gamma, gamma_d, e2
# code:gamma ends here

# [[file:../Empirics/regression.org::code:Ar_w][code:Ar_w]]
# Tangled on Tue Sep 26 10:57:34 2023
from scipy import sparse
from timeit import default_timer as timer

def estimate_w(y,beta,return_se=False,verbose=False):
    """
    Estimate regression $Mpi(Y - widehat{gamma(d)})  =  A(r) + hat{beta}w + e$.
    """
    try:
        y0 = y.stack()
    except AttributeError:
        y0 = y

    assert np.allclose(y0.groupby(['t','m']).mean(),0), "Pass Mpi(Y - gamma_d) to estimate_w."

    J = len(beta)

    beta = pd.DataFrame(beta)

    tm = [(t,m) for t in y0.index.levels[1] for m in y0.index.levels[2]]

    if len(y0.shape)==1 and y0.name is None: y0.name = 'y0'

    N = y0.index.levels[0]

    A = sparse.kron(sparse.kron(np.ones((len(N),1)),sparse.eye(len(tm))),np.ones((J,1)),format='csr')

    index = pd.MultiIndex.from_tuples([(i,t,m,j) for i in N for t,m in tm for j in beta.index.tolist()])

    A = pd.DataFrame.sparse.from_spmatrix(A,index=index)
    A.columns = pd.MultiIndex.from_tuples([(t,m) for t,m in tm])
    A.index.names = ['i','t','m','j']
    A.columns.names = ['t','m']

    cols = y0.groupby(['i','t','m']).mean().index

    index = pd.MultiIndex.from_tuples([(i[0],i[1],i[2],j) for i in cols.tolist() for j in beta.index.tolist()])

    B = sparse.kron(sparse.eye(len(cols)),beta,format='csr')
    B = pd.DataFrame.sparse.from_spmatrix(B,index=index,columns=cols)
    B.index.names = ['i','t','m','j']

    A = A.reindex(y0.index,axis=0)
    # This is very slow.
    B = B.reindex(y0.index,axis=0)

    X0 = pd.concat([A,B],axis=1)
    cols = X0.columns

    X0 = X0.sparse.to_coo()

    #start = timer()
    rslt = sparse.linalg.lsqr(X0,y0,atol=1e-16,btol=1e-16,show=verbose)
    #end = timer()
    #print("Time for lsqr %g" % (end-start,))
    b = pd.Series(rslt[0],index=cols)

    e = y0 - X0@b

    eg = e.groupby(['t','m','j'])

    Ar = eg.mean()
    Ar.name = 'Ar'

    # Missing data means that Ar.groupby(['t','m']).mean() may not be exactly zero; recenter.
    #Ar_bar = Ar.groupby(['t','m']).mean()
    #Ar = Ar - Ar_bar

    Ar_se = eg.std()/np.sqrt(eg.count())

    e3 = e - eg.transform(np.mean)

    what = pd.Series(b[len(A.columns):(len(A.columns)+len(B.columns))],index=B.columns)

    return what,Ar,Ar_se,e3
# code:Ar_w ends here

# [[file:../Empirics/regression.org::code:pi][code:pi]]
# Tangled on Tue Sep 26 10:57:34 2023
def estimate_pi(y,b,w,Ar,gamma_d,verbose=False):

    try:
        y0 = y.stack()
    except AttributeError:
        y0 = y.copy()

    wb = outer(w,b).stack()

    e = y0 - Ar - wb - gamma_d

    e = e.dropna()

    pi_g = e.groupby(['t','m'])

    pi = pi_g.mean()
    pi.name = 'pi'

    pi_se = pi_g.std()/np.sqrt(pi_g.count())

    assert np.all(pi_se>0), "Non-positive estimates of pi_se?!"

    e4 = e - pi
    e4 = e4.reorder_levels(['i','t','m','j']).sort_index()

    return pi, pi_se, e4
# code:pi ends here

# [[file:../Empirics/regression.org::code:predict][code:predict]]
# Tangled on Tue Sep 26 10:57:34 2023
def predict_y(pi,Ar,gamma_d,beta,wr):
    bwr = outer(wr,beta).stack()

    yhat = pi + Ar + gamma_d + bwr

    return yhat.reorder_levels(['i','t','m','j']).sort_index()
# code:predict ends here

# [[file:../Empirics/regression.org::code:data_preparation][code:data_preparation]]
# Tangled on Tue Sep 26 10:57:34 2023
from .df_utils import broadcast_binary_op
from .estimation import drop_columns_wo_covariance
import matplotlib.pyplot as plt
from types import SimpleNamespace

def prepare_data(y,d,min_obs=30,min_prop_items=0.1,alltm=False):
    assert y.index.names == ['i','t','m','j']

    # Drop household observations with fewer items than
    # min_prop_items*number of items
    Y = y.unstack('j')
    items = Y.count(axis=1)
    Y = Y[items>(min_prop_items*Y.shape[1])]

    if alltm:
        alltm = Y.groupby(['t','m']).count().replace(0,np.nan).dropna(axis=1).columns.tolist()
        Y = Y[alltm]

    y = Y.stack('j').dropna()


    # Make d a dataframe, with columns k
    if 'k' in d.index.names:
        d = d.unstack('k')

    # Match up rows of d with y
    YD = pd.DataFrame({'y':y}).join(d,how='left')

    YD = YD.dropna()

    y = YD['y']  # Drops expenditures that lack corresponding d

    # Drop goods from y if not enough observations to calculate
    # covariance matrix
    Y = drop_columns_wo_covariance(y.unstack('j'),min_obs=min_obs)

    y = Y.stack('j').dropna()

    # If no variation in d across j, collapse
    dg = YD.iloc[:,1:].groupby(['i','t','m'])
    if dg.std().mean().max()<1e-12:
        d = dg.head(1).droplevel('j') # And vice versa
        assert d.index.names == ['i','t','m']
        d.columns.name='k'

    return y,d

def find_optimal_K(y,d,shuffles=30,verbose=False):
    nstar = int(minimize_scalar(lambda k: -kmean_controls(k,Mp(y),Mp(d),
                                                          shuffles=30,
                                                          classifiers=d.loc[:,d.dtypes == 'category'],
                                                          verbose=verbose)[0],
                                    bracket=[1,20]).x)
    return nstar
# code:data_preparation ends here

# [[file:../Empirics/regression.org::*Construct Missing "correction"][Construct Missing "correction":1]]
# Tangled on Tue Sep 26 10:57:34 2023
def missing_correction(y,d,K=None,min_obs=None):
    M = 1-np.isnan(y.unstack('j'))  # Non-missing
    M = M.stack()

    M,d = prepare_data(M,d,min_obs=min_obs)

    R =  estimation(M,d,K=K,return_se=False)

    Mhat = predict_y(R['pi'],R['Ar'],R['gamma_d'],R['beta'],R['w'])

    R['M'] = M
    R['Mhat'] = Mhat

    e = M - Mhat
    R['R2'] = 1-e.var()/M.var()

    return e,R
# Construct Missing "correction":1 ends here

# [[file:../Empirics/regression.org::*Estimate][Estimate:1]]
# Tangled on Tue Sep 26 10:57:34 2023
import time

def estimation(y,d,K=None,beta=None,bootstrap_tol=None,return_se=False,rectify=False,verbose=False):

    if K is None: method = 'linear'
    else: method = 'categorical'

    if verbose:
        tic = time.time()
        print('Estimating MdMpy...')

    MdMpy,Md,MdMp,d = estimate_MdMpy(y,d,K)

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Estimating beta...')
        tic = toc

    if beta is None:# Estimate b
        hatb,seb,V = estimate_beta(MdMpy,
                                   return_se=return_se,
                                   bootstrap_tol=bootstrap_tol,
                                   verbose=verbose)
    else:
        hatb = beta
        seb = None

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Estimating Mpw...')
        tic = toc

    if return_se and bootstrap_tol is None:
        hatMpw, scale, mults, seb, mults_se, e1 = estimate_Mpw(y,hatb,MdMpy,return_se=True)
    else:
        hatMpw,scale,mults = estimate_Mpw(y,hatb,MdMpy,return_se=False)
        mults_se = mults*np.nan
        e1 = None

    # Scale bhat to match up with Mpw normalization
    hatb = (hatb*scale).squeeze()

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Estimating gamma...')
        tic = toc

    hatgamma, gamma_d, e2 = estimate_gamma(Mp(y),hatb,hatMpw,d,method=method)
    try:
        if d.columns.name is None:
            d.columns.name = 'k'
    except AttributeError:
        pass

    # y - hatgamma(d)
    y0 = (Mpi(y - gamma_d)).dropna()

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Estimating w, Ar...')
        tic = toc

    hatw, Ar, Ar_se, e3 = estimate_w(y0,hatb,verbose=verbose)
    #print('Ar,w')

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Estimating pi...')
        tic = toc

    hatpi, pi_se, e4 = estimate_pi(y,hatb,hatw,Ar,gamma_d,verbose=verbose)

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Estimating yhat...')
        tic = toc

    yhat = predict_y(hatpi,Ar,gamma_d,hatb,hatw)
    e = y - yhat.reindex_like(y)

    sigma2 = e.unstack('j').var()

    R2 = 1 - sigma2/y.unstack('j').var()

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Estimating gamma_se...')
        tic = toc

    if method=='linear':
        try:
            se_gamma = 1/np.sqrt((d.groupby('j').count()*(d.groupby('j').var() + d.groupby('j').mean()**2)).divide(sigma2,level='j',axis=0))
        except KeyError:  # d doesn't vary with j?
            se_gamma = np.sqrt((outer(sigma2,1/((d.var()+d.mean()**2)*d.count()))))
    else:
        se_gamma = None

    if rectify:
        if verbose:
            toc = time.time()
            print(f'[{toc-tic}] Rectifying...')
            tic = toc

        B,X = validate(y,hatpi,Ar,d,hatw,hatb,hatgamma,GramSchmidt=False)
        # Re-orthogonalize
        hatb = hatb*B['bw']
        if seb is not None:
            seb = seb*B['bw']
        Ar = Ar*B['Ar']
        Ar_se = Ar_se*B['Ar']
        hatpi = hatpi*(B['pi']@y.groupby('j').count()/y.shape[0])
        pi_se = pi_se*(B['pi']@y.groupby('j').count()/y.shape[0])
        try:
            hatgamma = (hatgamma.stack()*B['gamma_d']).unstack('k')
            if se_gamma is not None:
                se_gamma = (se_gamma.stack()*B['gamma_d']).unstack('k')
        except AttributeError:
            hatgamma = hatgamma*B['gamma_d']
            if se_gamma is not None:
                se_gamma = se_gamma*B['gamma_d']
    else:
        B = None
        X = None

    if verbose:
        toc = time.time()
        print(f'[{toc-tic}] Finishing...')
        tic = toc

    # Convert tuples in index  to strings (necessary for persistence in sql)
    if hatgamma.index.name == 'tau':
        hatgamma.index = [str(s) for s in hatgamma.index]
        hatgamma.index.name = 'k'

    if return_se:
        mults_se = mults_se.unstack('m')
        pi_se = pi_se.unstack('m')
        Ar_se = Ar_se.unstack(['t','m'])
    else:
        mults_se = None
        pi_se = None
        Ar_se = None

    return dict(y=y,
                yhat=yhat,
                mse=(e**2).mean(),
                R2=R2,
                d=d,
                beta=hatb,
                beta_se=seb,
                beta_V=V,
                mults = mults,
                mults_se = mults_se,
                e1 = e1,
                w = hatw,
                e3 = e3,
                Mpw = hatMpw,
                gamma = hatgamma,
                gamma_se = se_gamma,
                e2 = e2,
                gamma_d = gamma_d,
                pi = hatpi,
                pi_se = pi_se,
                e4 = e4,
                Ar = Ar,
                Ar_se = Ar_se,
                B=B,
                X=X)
# Estimate:1 ends here

# [[file:../Empirics/regression.org::*Validate][Validate:1]]
# Tangled on Tue Sep 26 10:57:34 2023

def validate(y,pi,Ar,d,w,beta,gamma,GramSchmidt=False):
    def ols(x):
        y = x['y']
        x = x.drop('y',axis=1)

        y,x = drop_missing([y,x])

        b = np.linalg.lstsq(x,y,rcond=None)[0]

        return pd.Series(b.squeeze(),index=x.columns)

    X = pd.merge(Ar.reset_index('j'),pi,on=['t','m']).reset_index().set_index(['t','m','j'])

    if gamma.index.name=='tau':
        gamma_d = pd.DataFrame(d).join(gamma,on='tau')
        gamma_d.columns.name = 'j'
        gamma_d = gamma_d.drop('tau',axis=1)
        gamma_d = gamma_d.stack()
    else:
        gamma_d = inner(d,gamma,['i','t','m','j'],[])

    gamma_d.name = 'gamma_d'
    gamma_d = gamma_d[y.index]

    if GramSchmidt:
        gamma_d = Mp(gamma_d)

    if 'j' in gamma_d.index.names:
        X = pd.merge(X,gamma_d.reset_index(['i']),left_on=['t','m','j'],right_on=['t','m','j'],how='outer')
    else:
        X = pd.merge(X.reset_index('j'),gamma_d.reset_index(['i']),left_on=['t','m'],right_on=['t','m'],how='outer')

    X = X.rename(columns={('i',''):'i'}) # Deal with bug in reset_index for sparse matrices?

    X = X.reset_index().set_index(['i','t','m','j'])

    w.name='w'

    bw = outer(w,beta).stack()
    bw.name = 'bw'

    if GramSchmidt:
        MdMp = lambda x: Md_generator(x,d,Mp=True)
        bw = Mp(MdMp(bw))
        bw.name = 'bw'

    X = X.join(bw[y.index])

    X['y'] = y
    X = X.dropna()
    X.columns.name = 'l'

    B = X.groupby('j').apply(lambda x: ols(x))

    return B,X
# Validate:1 ends here

# [[file:../Empirics/regression.org::regression_class][regression_class]]
# Tangled on Tue Sep 26 10:57:34 2023
import numpy as np
import pandas as pd
import warnings
from sqlalchemy import create_engine
from pathlib import Path
from collections import namedtuple, OrderedDict
from cfe.df_utils import is_none

# Names of Series & DataFrames which are attributes of a Regression object

arrs = {'y':('itmj',),      # Log expenditures, (itm,j)
        'd':('itm','k'),      # Household characteristics (itm,k)
        'alpha':("j",),
        'beta':("j",),   # Frisch elasticities, (j,)
        'gamma':('j','k'),  # Coefficients on characteristics (k,)
        'alpha_se':('j',),
        'beta_se':('j',),
        'gamma_se':('j','k'),
        'beta_V':('j','jp'),
        'w':('itm',),
        'yhat':('itmj',),
        'e':('itmj',),
        'pi':('t','m'),
        'pi_se':('t','m'),
        'mults':('t','m'),
        'mults_se':('t','m'),
        'e1':('itmj',),
        'e2':('itmj',),
        'e3':('itmj',),
        'e4':('itmj',),
        'Mpw':('itm',),
        'gamma_d':('j','k'),
        'Ar':('j','tm'),
        'Ar_se':('j','tm'),
        'B':('j','l'),
        'X':('itmj','l'),
         }

class Regression:
    """
    A class which packages together data and methods for estimating a CFE demand system posed as a regression.

    Data elements (and outputs) are typically pandas Series or DataFrames.  Indexes are kept consistent across objects, with:
       - i :: Indexes households
       - t :: Indexes periods
       - m :: Indexes markets
       - j :: Indexes goods
       - k :: Indexes household characteristics

    Ethan Ligon                               October 2022
    """


    __slots__ = list(arrs.keys()) + ['attrs','Md','MdMp','Mp']

    def __init__(self,
                 correct_miss=False,
                 method='linear',
                 K=None,
                 bootstrap_tol=None,
                 return_se=False,
                 rectify=False,
                 verbose=False,
                 min_obs=30,
                 min_prop_items=0.1,
                 alltm=True,
                 **kwargs):
        """To load data, use cfe.read_sql() or cfe.read_pickle().

        To instantiate from data on log expenditures (y) and household
        characteristics (d), supply each as pd.DataFrames, with indices for y
        (i,t,m) and columns (j,) and for d indices (i,t,m) and columns (k,).
        """

        for k in self.__slots__:
            if k in kwargs.keys():
                setattr(self,k,kwargs[k])
            else:
                setattr(self,k,None)

        attrs={}
        attrs['correct_miss'] = correct_miss
        attrs['method'] = method
        attrs['K'] = K
        attrs['bootstrap_tol'] = bootstrap_tol
        attrs['return_se'] = return_se
        attrs['rectify'] = rectify
        attrs['verbose'] = verbose
        attrs['min_obs'] = min_obs
        attrs['min_prop_items'] = min_prop_items
        attrs['alltm'] = alltm

        self.attrs=attrs

        if 'y' in kwargs.keys() and 'd' in kwargs.keys():
            self.y,self.d = prepare_data(self.y,self.d,min_obs=min_obs,
                                         min_prop_items=min_prop_items,
                                         alltm=alltm)
# regression_class ends here

# [[file:../Empirics/regression.org::*Estimate][Estimate:1]]
# Tangled on Tue Sep 26 10:57:34 2023
    def estimate(self,beta=None):

        if beta is not None:
            beta = pd.DataFrame(beta)

        R = estimation(self.y,self.d,
                       K=self.attrs['K'],
                       beta=beta,
                       bootstrap_tol=self.attrs['bootstrap_tol'],
                       return_se=self.attrs['return_se'],
                       rectify=self.attrs['rectify'],
                       verbose=self.attrs['verbose'])

        for k,v in R.items():
            try:
                if getattr(self,k) is not None: continue
                setattr(self,k,v)
            except AttributeError:
                setattr(self,k,v)
# Estimate:1 ends here

# [[file:../Empirics/regression.org::*Persistence][Persistence:1]]
# Tangled on Tue Sep 26 10:57:34 2023
    def to_sql(self,fn=None,overwrite=False):
        """
        Save to sql database fn.
        """
        if overwrite: if_exists = 'replace'
        else: if_exists = 'fail'

        if fn is not None:
            if not Path(fn).is_absolute():
                fn = str(Path(__file__).absolute().parent.joinpath(fn))
            loc = f'sqlite:///{fn}'
        else:
            loc = f'sqlite://'

        engine = create_engine(loc, echo=False)
        with engine.begin() as connection:
            try:
                for k in arrs.keys():
                    try:
                        x = getattr(self,k)
                        if x is not None:
                            x.to_sql(k,connection,if_exists=if_exists)
                    except AttributeError:
                        continue
                pd.Series(self.attrs).to_sql('attrs',connection,if_exists=if_exists)
            except ValueError:
                raise IOError("To_sql would overwrite existing data.  Pass 'overwrite=True' if this is what you want.") from None

    def to_pickle(self,fn):
        """
        Write dictionary of attributes to a pickle.
        """
        d = {}
        for attr in self.__dir__():
            try:
                x = getattr(self,attr)
                x.shape
                d[attr] = x
            except AttributeError: continue

            d['attrs'] = self.attrs

        pd.to_pickle(d,fn)
# Persistence:1 ends here

# [[file:../Empirics/regression.org::*Accessors][Accessors:1]]
# Tangled on Tue Sep 26 10:57:34 2023
    def get_MdMpy(self):
        MdMpy,Md,MdMp,d = estimate_MdMpy(self.y,self.d,self.attrs['K'])

        self.d = d

        self.MdMp = MdMp
        self.Md = Md

        return MdMpy

    def get_beta(self,verbose=None,return_se=None,bootstrap_tol=1e-2,heteroskedastic=False):
        """
        Return beta, or if return_se=True, return beta_se.
        If standard errors are computed obtain Variance matrix as a side-effect.
        """
        if return_se is None:
            return_se = self.attrs['return_se']

        if return_se:
            if self.beta_se is not None:
                return self.beta_se
        else:
            if self.beta is not None:
                return self.beta

        MdMpy = self.get_MdMpy()
        if verbose is None:
            verbose = self.attrs['verbose']

        b, seb, V = estimate_beta(MdMpy,verbose=verbose,return_se=return_se,bootstrap_tol=bootstrap_tol,heteroskedastic=heteroskedastic)
        b = b.squeeze()
        if seb is not None:
            self.beta_se = seb.squeeze()
            self.beta_V = V

        self.beta = b

        if return_se:
            return self.beta_se
        else:
            return self.beta

    def get_gamma(self,verbose=None):

        if self.gamma is not None:
            return self.gamma
        else:
            gd = get_gamma_d(self,verbose=verbose)
            return self.gamma

    def get_gamma_d(self,verbose=None):

        if self.gamma_d is not None:
            return self.gamma_d

        if self.MdMp is None:
            MdMpy = self.get_MdMpy()

        if verbose is None:
            verbose = self.attrs['verbose']

        b,Mpw,seb,mults,mults_se,e1 = estimate_beta_and_Mpw(self.y,self.MdMp,
                                      return_se=self.attrs['return_se'],
                                      bootstrap_tol=self.attrs['bootstrap_tol'],
                                      verbose=verbose)

        if self.beta is None: self.beta = b.squeeze()
        if self.Mpw is None: self.Mpw = Mpw
        if seb is not None:
            if self.beta_se is None: self.beta_se = seb.squeeze()

        if self.mults is None: self.mults = mults.squeeze()
        if mults_se is not None:
            if self.mults_se is None: self.mults_se = mults_se.squeeze()
        if self.e1 is None: self.e1 = e1

        gamma,gamma_d,e2 = estimate_gamma(Mp(self.y),self.beta,self.Mpw,self.d,
                                          method=self.attrs['method'],
                                          verbose=verbose)

        if self.gamma is None: self.gamma = gamma
        if self.e2 is None: self.e2 = e2
        if self.gamma_d is None: self.gamma_d = gamma_d

        return self.gamma_d

    def get_w(self,verbose=None):
        """
        Estimate welfare weights $w$.
        """
        if self.w is not None:
            return self.w

        if verbose is None:
            verbose = self.attrs['verbose']

        gamma_d = self.get_gamma_d(verbose=verbose)

        y0 = (Mpi(self.y - gamma_d)).dropna()

        b = self.get_beta(verbose=verbose)

        w,Ar,Ar_se,e3 = estimate_w(y0,b,verbose=verbose)

        self.w = w
        if self.Ar is None: self.Ar = Ar
        if self.Ar_se is None: self.Ar_se = Ar_se
        if self.e3 is None: self.e3 = e3

        return self.w

    def get_Ar(self,verbose=None):
        """
        Estimate relative prices.
        """
        if self.Ar is not None:
            return self.Ar

        if verbose is None:
            verbose = self.attrs['verbose']

        # Estimation of w also computes Ar
        self.get_w(verbose=verbose)

        return self.Ar


    def get_pi(self,verbose=None):
        """
        Estimate price index.
        """
        if self.pi is not None:
            return self.pi

        if verbose is None:
            verbose = self.attrs['verbose']

        b = self.get_beta(verbose=None)
        gamma_d = self.get_gamma_d(verbose=verbose)

        w = self.get_w(verbose=verbose)

        Ar = self.get_Ar(verbose=verbose)

        hatpi, pi_se, e4 = estimate_pi(self.y,b,w,Ar,gamma_d,verbose=verbose)
        self.pi = hatpi
        self.pi_se = pi_se
        self.e4 = e4

        return self.pi


    def get_predicted_log_expenditures(self,fill_missing=True,verbose=None):
        """
        Expected log expenditures.

        - fill_missing :: Make predictions even when observations on actual log expenditures are missing.  Default True.
        - verbose :: Default False.
        """
        if self.yhat is not None:
            return self.yhat

        if verbose is None:
            verbose = self.attrs['verbose']

        gamma_d = self.get_gamma_d(verbose=verbose)

        b = self.get_beta(verbose=verbose)

        w = self.get_w(verbose=verbose)

        Ar = self.get_Ar(verbose=verbose)

        pi = self.get_pi(verbose=verbose)

        self.yhat = predict_y(pi,Ar,gamma_d,b,w)

        if fill_missing:
            return self.yhat
        else:
            return (self.yhat + self.y*0).dropna()

    def get_gamma_se(self):
        if self.gamma_se is not None: return self.gamma_se

        e = self.y - self.get_predicted_log_expenditures(fill_missing=False)

        d = self.d

        sigma2 = e.unstack('j').var()

        if self.attrs['method']=='linear':
            try:
                self.gamma_se = 1/np.sqrt((d.groupby('j').count()*(d.groupby('j').var() + d.groupby('j').mean()**2)).divide(sigma2,level='j',axis=0))
            except KeyError:  # d doesn't vary with j?
                self.gamma_se = np.sqrt((outer(sigma2,1/((d.var()+d.mean()**2)*d.count()))))

        return self.gamma_se
# Accessors:1 ends here

# [[file:../Empirics/regression.org::*Other methods][Other methods:1]]
# Tangled on Tue Sep 26 10:57:34 2023
    def validate(self,rectify=False,GramSchmidt=False,verbose=False):
        B,X = validate(self.y,
                       self.pi,
                       self.Ar,
                       self.d,
                       self.w,
                       self.beta,
                       self.gamma,
                       GramSchmidt=GramSchmidt)

        # Re-orthogonalize
        if rectify:
            self.yhat = None
            self.beta = self.beta*B['bw']
            if self.beta_se is not None:
                self.beta_se = self.beta_se*B['bw']
            self.Ar = self.Ar*B['Ar']
            self.Ar_se = self.Ar_se*B['Ar']
            self.pi = self.pi*(B['pi']@self.y.groupby('j').count()/self.y.shape[0])
            self.pi_se = self.pi_se*np.abs(B['pi']@self.y.groupby('j').count()/self.y.shape[0])
            try:
                self.gamma = (self.gamma.stack()*B['gamma_d']).unstack('k')
                if self.gamma_se is not None:
                    self.gamma_se = (self.gamma_se.stack()*np.abs(B['gamma_d'])).unstack('k')
            except AttributeError:
                self.gamma = self.gamma*B['gamma_d']
                if self.gamma_se is not None:
                    self.gamma_se = self.gamma_se*np.abs(B['gamma_d'])
        return B

    def mse(self):
        """
        Mean-squared error of estimates.
        """
        if self.yhat is None:
            self.get_predicted_log_expenditures()
        try:
            return ((self.y - self.yhat)**2).mean()
        except AttributeError:
            self.get_predicted_log_expenditures()
            return mse(self)

    def R2(self,summary=False):
        yhat = self.get_predicted_log_expenditures(fill_missing=False)

        e = self.y - yhat.reindex_like(self.y)

        if summary:
            sigma2 = e.var()

            R2 = 1 - sigma2/self.y.var()
        else:
            sigma2 = e.unstack('j').var()

            R2 = 1 - sigma2/self.y.unstack('j').var()

        return R2

    def optimal_number_of_clusters(self):
        """
        Find optimal number of clusters for K-means.
        """
        self.flags['K'] = find_optimal_K(self.y,self.d)

    def predicted_expenditures(self,resample=False,clusterby=['t','m','j'],fill_missing=True,verbose=False):
        """Compute predicted /levels/ of expenditures.

        This is different from exp(yhat), since we have to account for the expected value of exp(e), where e = y - yhat.

        One standard (and the default) way to calculate these is by assuming that the distribution of e is normal.  An alternative is to resample residuals.

        Regardless of whether resampling is chosen, means (and variances) are selected at the level of the list clusterby.
        """
        if self.yhat is None:
            self.yhat = self.get_predicted_log_expenditures(fill_missing=fill_missing,verbose=verbose)

        e = self.y - self.yhat
        eg = e.dropna().groupby(clusterby)

        if not resample:
            # Use iqr instead of variance for some robustness to outliers
            # Relation for normal dist: iqr/1.3489795 = sigma
            evar = (eg.transform(iqr)/1.3489795)**2
        else:
            if resample < 1: # Assume this is a tolerance
                tol = resample
            last = -1
            evar = e.dropna().groupby(clusterby).transform(np.var)
            evar = evar.sort_index(level=clusterby)
            i = 0
            diff = 1
            while diff>tol:
                last = evar
                esample = eg.sample(frac=1,replace=True)
                drawvar = (esample.groupby(clusterby).transform(iqr)/1.3489795)**2
                evar = i/(i+1)*evar + drawvar.values/(i+1)
                i += 1
                diff = np.abs(evar-last).max()
                if verbose: print(f'Draw {i}, diff={diff}')

        if fill_missing:
            evar = evar.groupby(clusterby).mean()
            xhat = np.exp(self.yhat.add(evar/2))
            xhat = xhat.reorder_levels(self.yhat.index.names).sort_index()
        else:
            xhat = np.exp(self.yhat + evar/2)
            xhat = xhat.reorder_levels(self.yhat.index.names).sort_index()

        return xhat
# Other methods:1 ends here

# [[file:../Empirics/regression.org::*Presentation methods][Presentation methods:1]]
# Tangled on Tue Sep 26 10:57:34 2023
    def graph_beta(self,fn=None,xlabel='Frisch Elasticities',heteroskedastic=False):
        import matplotlib.pyplot as plt

        if self.beta is None or self.beta_se is None:
            self.get_beta(return_se=True,heteroskedastic=heteroskedastic)

        beta = self.beta.sort_values()
        se = self.beta_se

        # Sort se to match beta
        se = se[beta.index]

        # Want about 1/8" vertical space per good
        fig,ax = plt.subplots(figsize=(8,1+len(beta)/8))

        ax.errorbar(beta,range(len(beta)), xerr=se)
        ax.set_xlabel(xlabel)

        ax.set_yticks(list(range(len(beta))))
        ax.set_yticklabels(beta.index.values.tolist(),rotation=0,size='small')

        if fn is not None:
            fig.savefig(fn,bbox_inches='tight')

        return fig
# Presentation methods:1 ends here

# [[file:../Empirics/regression.org::regression_demand_interface][regression_demand_interface]]
# Tangled on Tue Sep 26 10:57:34 2023
import consumerdemands
import pandas as pd

def _demand_parameters(self,p=None,d=None):
    """Return tuple of p and dictionary of (alpha,beta,phi) from regression instance.

    Suitable for passing to =cfe.demand= functions.
    """

    beta = self.beta
    n = len(beta)

    if d is None:
        gd = self.get_gamma_d().groupby('j').mean()
    else:
        gd = d@self.gamma.T

    alpha = np.exp(gd)

    if p is None or len(p)==0:
        prices = np.exp((self.pi + self.Ar).groupby('j').mean())
    else:
        prices = p

    assert len(prices), f"What happened to prices? p={prices}."

    phi = 0 # phi not (yet?) an attribute of Regression.

    return prices,{'alpha':alpha,'beta':beta,'phi':phi}

def _lambdavalue(self,x,p=None,z=None):
    """Marginal utility at expenditures x.
    """

    p,pparms = _demand_parameters(self,p,z)

    return consumerdemands.lambdavalue(x,p,pparms)

def _demands(self,x,p=None,z=None,type="Marshallian"):
    """Quantities demanded at prices p for household with observable
    characteristics z, having a utility function with parameters given
    by (possibly estimated) attributes from a Regression (i.e., the
    vectors of parameters alpha, beta, delta).

    Default type is "Marshallian", in which case argument x is budget.

    Alternative types:
       - "Frischian" :: argument x is Marginal utility of expenditures
       - "Hicksian" :: argument x is level of utility

    Ethan Ligon                                    April 2019
    """

    p,pparms = _demand_parameters(self,p,z)

    Qs = {'Marshallian':consumerdemands.marshallian.demands,
          'Hicksian':consumerdemands.hicksian.demands,
          'Frischian':consumerdemands.frischian.demands}

    q = pd.Series(Qs[type](x,p,pparms),index=pparms['alpha'].index,name='quantities')

    return q

def _expenditures(self,x,p=None,z=None,type='Marshallian'):
    """Expenditures for different goods at prices p for household with observable
    characteristics z, having a utility function with parameters given
    by (possibly estimated) attributes from a Regression (i.e., the
    vectors of parameters alpha, beta, delta).

    Default type is "Marshallian", in which case argument x is budget.

    Alternative types:
       - "Frischian" :: argument x is Marginal utility of expenditures
       - "Hicksian" :: argument x is level of utility

    Ethan Ligon                                    April 2023
    """

    p,pparms = _demand_parameters(self,p,z)

    q = _demands(self,x,p=p,z=z,type=type)

    return p*q


def _utility(self,x,p=None,z=None,type="Marshallian"):
    """(Indirect) utility

    Level of utility at prices p for household with observable
    characteristics z, having a utility function with parameters given
    by (possibly estimated) attributes from a Regression (i.e., the
    vectors of parameters alpha, beta, delta).

    Default type is "Marshallian", in which case argument x is budget.

    Alternative types:
       - "Frischian" :: argument x is Marginal utility of expenditures
       - "Hicksian" :: argument x is level of utility

    Ethan Ligon                                    April 2019
    """

    p,pparms = _demand_parameters(self,p,z)

    Us = {'Marshallian':consumerdemands.marshallian.indirect_utility,
          'Hicksian': lambda U,**xargs: U,
          'Frischian':consumerdemands.frischian.indirect_utility}

    return Us[type](x,p,pparms)

def _expenditurefunction(self,x,p=None,z=None,type='Hicksian'):
    """Total Expenditures

    Expenditures at prices p for household with observable
    characteristics z, having a utility function with parameters given
    by (possibly estimated) attributes from a Regression (i.e., the
    vectors of parameters alpha, beta, delta).

    Default type is "Hicksian", in which case argument x is level of utility U.

    Alternative types:
       - "Frischian" :: argument x is Marginal utility of expenditures
       - "Marshallian" :: argument x is expenditures.

    Ethan Ligon                                    April 2019
    """

    p,pparms = _demand_parameters(self,p,z)

    Xs = {'Marshallian': lambda U,**xargs: U,
          'Hicksian': consumerdemands.hicksian.expenditurefunction,
          'Frischian':consumerdemands._core.expenditures}

    return Xs[type](x,p,pparms)

def _relative_risk_aversion(self,p=None,z=None):
    """Returns relative risk aversion =function= that varies with =x=.

    Varies with prices p, and observablecharacteristics z.

    Ethan Ligon                                    December 2022
    """

    p,pparms = _demand_parameters(self,p,z)

    return consumerdemands.demands.relative_risk_aversion(p,pparms)

Regression.consumerdemands = consumerdemands
Regression.demands = _demands
Regression.expenditures = _expenditures
Regression.demand_parameters = _demand_parameters
Regression.lambdavalue = _lambdavalue
Regression.indirect_utility = _utility
Regression.expenditure = _expenditurefunction
Regression.relative_risk_aversion = _relative_risk_aversion
# regression_demand_interface ends here

# [[file:../Empirics/regression.org::*=read_sql=][=read_sql=:1]]
# Tangled on Tue Sep 26 10:57:34 2023
from sqlalchemy import inspect, create_engine
from ast import literal_eval as make_tuple

def read_sql(fn):
    """
    Read Regression object from file fn.
    """
    if not Path(fn).is_absolute():
        fn = str(Path(__file__).absolute().parent.joinpath(fn))
    loc = f'sqlite:///{fn}'
    engine = create_engine(loc, echo=False)

    inspector = inspect(engine)

    R = {}
    with engine.begin() as connection:
        for t in inspector.get_table_names():
            R[t] = pd.read_sql(t,connection)
            try:
                R[t] = R[t].set_index(list(arrs[t][0])).squeeze()
                if len(R[t].shape)>1: # still a dataframe
                    colnames = []
                    for l in arrs[t][1]:
                        if l not in R[t].columns:
                            colnames.append(l)
                        else:
                            R[t] = R[t].stack(l)
                    if len(colnames)==1: # Just an index
                        R[t].columns.names = colnames
                    else: # Need a multiindex
                        cols = [make_tuple(s) for s in R[t].columns]
                        R[t].columns = pd.MultiIndex.from_tuples(cols,names=colnames)
            except KeyError:
                pass

        if not len(R):
            raise OSError(f'Trying to read empty file?  Check {loc}.')

    return Regression(**R)
# =read_sql=:1 ends here

# [[file:../Empirics/regression.org::*=read_pickle=][=read_pickle=:1]]
# Tangled on Tue Sep 26 10:57:34 2023
import pickle

def read_pickle(fn,cache_dir=None):
    """
    Read pickled dictionary and assign keys as attributes to Regression object.
    """
    import fsspec

    try:
        R = pickle.load(fn)  # Is fn a file?
    except TypeError:  # Maybe a filename?
        if cache_dir is not None:
            if 'filecache::' not in fn:  # May already have caching specified
                fn = 'filecache::' + fn
            storage_options = {'filecache':{'cache_dir':cache_dir}}
            with fsspec.open(fn,mode='rb',
                             storage_options=storage_options) as f:
                R = pickle.load(f)
        else:
            with fsspec.open(fn,mode='rb') as f:
                R = pickle.load(f)

    if type(R) is not dict:
        R = R.__dict__
        # Fix ill-considered attribute name
        try:
            R['mults_se'] = R['se_mult']
            del R['se_mult']
        except KeyError:
            pass

    return Regression(**R)
# =read_pickle=:1 ends here
