import numpy as np
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import random
from typing import List


def Hbeta(D=np.array([]), beta=1.0):
    """
        Compute the perplexity and the P-row for a specific value of the
        precision of a Gaussian distribution.
    """

    # Compute P-row and corresponding perplexity
    P = np.exp(-D.copy() * beta)
    sumP = sum(P)
    H = np.log(sumP) + beta * np.sum(D * P) / sumP
    P = P / sumP
    return H, P


def x2p(X=np.array([]), tol=1e-5, perplexity=30.0):
    """
        Performs a binary search to get P-values in such a way that each
        conditional Gaussian has the same perplexity.
    """

    # Initialize some variables
    print("Computing pairwise distances...")
    (n, d) = X.shape
    sum_X = np.sum(np.square(X), 1)
    D = np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X)
    P = np.zeros((n, n))
    beta = np.ones((n, 1))
    logU = np.log(perplexity)

    # Loop over all datapoints
    for i in range(n):

        # Print progress
        if i % 500 == 0:
            print("Computing P-values for point %d of %d..." % (i, n))

        # Compute the Gaussian kernel and entropy for the current precision
        betamin = -np.inf
        betamax = np.inf
        Di = D[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))]
        (H, thisP) = Hbeta(Di, beta[i])

        # Evaluate whether the perplexity is within tolerance
        Hdiff = H - logU
        tries = 0
        while np.abs(Hdiff) > tol and tries < 50:

            # If not, increase or decrease precision
            if Hdiff > 0:
                betamin = beta[i].copy()
                if betamax == np.inf or betamax == -np.inf:
                    beta[i] = beta[i] * 2.
                else:
                    beta[i] = (beta[i] + betamax) / 2.
            else:
                betamax = beta[i].copy()
                if betamin == np.inf or betamin == -np.inf:
                    beta[i] = beta[i] / 2.
                else:
                    beta[i] = (beta[i] + betamin) / 2.

            # Recompute the values
            (H, thisP) = Hbeta(Di, beta[i])
            Hdiff = H - logU
            tries += 1

        # Set the final row of P
        P[i, np.concatenate((np.r_[0:i], np.r_[i+1:n]))] = thisP

    # Return final P-matrix
    print("Mean value of sigma: %f" % np.mean(np.sqrt(1 / beta)))
    return P


def pca(X=np.array([]), no_dims=50):
    """
        Runs PCA on the NxD array X in order to reduce its dimensionality to
        no_dims dimensions.
    """

    print("Preprocessing the data using PCA...")
    (n, d) = X.shape
    X = X - np.tile(np.mean(X, 0), (n, 1))
    (l, M) = np.linalg.eig(np.dot(X.T, X))
    Y = np.dot(X, M[:, 0:no_dims])
    return Y


def tsne(X=np.array([]), no_dims=2, initial_dims=50, perplexity=30.0):
    """
        Runs t-SNE on the dataset in the NxD array X to reduce its
        dimensionality to no_dims dimensions. The syntaxis of the function is
        `Y = tsne(X, no_dims, initial_dim, perplexity), where X is an NxD NumPy array.
    """

    # Check inputs
    if isinstance(no_dims, float):
        print("Error: array X should have type float.")
        return -1
    if round(no_dims) != no_dims:
        print("Error: number of dimensions should be an integer.")
        return -1

    # Initialize variables
    X = pca(X, initial_dims).real
    (n, d) = X.shape
    max_iter = 500
    initial_momentum = 0.5
    final_momentum = 0.8
    eta = 500
    min_gain = 0.01
    Y = np.random.randn(n, no_dims)
    dY = np.zeros((n, no_dims))
    iY = np.zeros((n, no_dims))
    gains = np.ones((n, no_dims))

    # Compute P-values
    P = x2p(X, 1e-5, perplexity)
    P = P + np.transpose(P)
    P = P / np.sum(P)
    P = P * 4.									# early exaggeration
    P = np.maximum(P, 1e-12)

    # Run iterations
    for iter in range(max_iter):

        # Compute pairwise affinities
        sum_Y = np.sum(np.square(Y), 1)
        num = -2. * np.dot(Y, Y.T)
        num = 1. / (1. + np.add(np.add(num, sum_Y).T, sum_Y))
        num[range(n), range(n)] = 0.
        Q = num / np.sum(num)
        Q = np.maximum(Q, 1e-12)

        # Compute gradient
        PQ = P - Q
        for i in range(n):
            dY[i, :] = np.sum(np.tile(PQ[:, i] * num[:, i], (no_dims, 1)).T * (Y[i, :] - Y), 0)

        # Perform the update
        if iter < 20:
            momentum = initial_momentum
        else:
            momentum = final_momentum
        gains = (gains + 0.2) * ((dY > 0.) != (iY > 0.)) + \
                (gains * 0.8) * ((dY > 0.) == (iY > 0.))
        gains[gains < min_gain] = min_gain
        iY = momentum * iY - eta * (gains * dY)
        Y = Y + iY
        Y = Y - np.tile(np.mean(Y, 0), (n, 1))

        # Compute current value of cost function
        if (iter + 1) % 100 == 0:
            C = np.sum(P * np.log(P / Q))
            print("Iteration %d: error is %f" % (iter + 1, C))

        # Stop lying about P-values
        if iter == 100:
            P = P / 4.

    # Return solution
    return Y


# Automatic ideal cluster detection
def deter_clusters(X, rng):
    WCSS = []
    for i in range(1, rng):
        kmeans = KMeans(i)
        kmeans.fit(X)
        WCSS.append(kmeans.inertia_)

    secondDerivative = [0 for i in range(len(WCSS))]
    for i in range(1, len(WCSS)-1):
        secondDerivative[i] = WCSS[i+1] + WCSS[i-1] - 2 * WCSS[i]
    
    optimal_clusters = secondDerivative.index(max(secondDerivative))+2
    return optimal_clusters, secondDerivative, WCSS


# Perform KMeans clustering on the data
def cluster_data(X, clusters):
    num_clusters = clusters
    kmeans = KMeans(num_clusters)
    kmeans.fit(X)
    labels = list(kmeans.labels_)
    return labels


# Simple Stratification
def stratified_selection(labels: List):
    '''
    Simple stratified selection.

    Args:
    labels: List()    # List of labels

    Returns:

    selected: List()  # List of selected indices
    '''
    selection_pool = dict()
    for i in range(len(labels)):
        if labels[i] not in list(selection_pool.keys()):
            selection_pool[labels[i]] = []
        selection_pool[labels[i]].append(i)

    selected = []

    for key in selection_pool.keys():
        num_samples = int(len(selection_pool[key])*.1)
        samples = random.sample(selection_pool[key], num_samples)
        selected.extend(samples)
    
    return selected


# Clustering with stratified selection
def stratified_selection_from_clusters(X: np.ndarray, clusters: int, final_features: int = 2, start_features: int = 50, perplexity: float = 30.0, sklearn: bool = True):
    '''
    Stratified selection using clustering.

    Args:
    X: np.ndarray       # Data
    clusters: int       # Number of clusters
    final_features: int # Number of features that will be used for clustering
    start_features: int # Features to be extracted from PCA
    perplexity: float   # The perplexity is related to the number of nearest neighbors that
                        is used in other manifold learning algorithms. Larger datasets
                        usually require a larger perplexity. Consider selecting a value
                        between 5 and 50. Different values can result in significantly
                        different results. The perplexity must be less than the number
                        of samples.
    sklearn: bool       # Use sklearn implementation True/False

    Returns:
    selected: List()    # List of selected indices
    '''
    # Run TSNE
    if sklearn:
        # Sklearn Implementation
        Y = TSNE(n_components=final_features, learning_rate='auto', perplexity=perplexity).fit_transform(X)
    else:
        # Orignal Implementation
        Y = tsne(X, final_features, start_features, perplexity)
    # Supervised learning 
    labels = cluster_data(Y, clusters)
    # Select indices
    selected = stratified_selection(labels)

    return selected


# Auto Clustering with stratified selection
def stratified_selection_from_auto_clusters(X: np.ndarray, cluster_range: int, final_features: int = 2, start_features: int = 50, perplexity: float = 30.0, sklearn: bool = True):
    '''
    Stratified selection using auto clustering. Here the ideal clusters are determined automatically.
    The user needs to specify the range in which he wants to find ideal clusters. 
    The ideal number of clusters are determined using the elbow method.

    Args:
    X: np.ndarray       # Data
    clusters_range: int # Number of clusters
    final_features: int # Number of features that will be used for clustering
    start_features: int # Features to be extracted from PCA
    perplexity: float   # The perplexity is related to the number of nearest neighbors that
                        is used in other manifold learning algorithms. Larger datasets
                        usually require a larger perplexity. Consider selecting a value
                        between 5 and 50. Different values can result in significantly
                        different results. The perplexity must be less than the number
                        of samples.
    sklearn: bool       # Use sklearn implementation True/False

    Returns:
    selected: List()    # List of selected indices
    '''
    
    # Run TSNE
    if sklearn:
        # Sklearn Implementation
        Y = TSNE(n_components=final_features, learning_rate='auto', perplexity=perplexity).fit_transform(X)
    else:
        # Orignal Implementation
        Y = tsne(X, final_features, start_features, perplexity)
    # Unsupervised learning 
    clusters, secondDerivative, WCSS = deter_clusters(Y, cluster_range)
    labels = cluster_data(Y, clusters)
    # Select indices
    selected = stratified_selection(labels)

    return selected