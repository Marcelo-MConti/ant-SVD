import numpy as np
from .jacobi import Jacobi_Decomposition


def Sort_By_Eigenvalue_Desc(eigenValues, eigenVectors):
    idx = np.argsort(eigenValues)[::-1]
    eigenValues = eigenValues[idx]
    eigenVectors = eigenVectors[:, idx]
    return eigenValues, eigenVectors 


def Compute_Rank(eigenValues, tolerance=1e-10):
    rank = 0
    for k in range(len(eigenValues)):
        if eigenValues[k] > tolerance:
            rank += 1
    return rank


def Valid_Rank(rank):
    return rank > 0


def Compute_U_From_SVD_Components(A, sigma, V, m, rank):
    U = np.zeros((m, rank))
    for i in range(rank):
        U[:, i] = (A @ V[:, i]) / sigma[i]
    return U

def Cumulative_Variance(eigenValueSquare, k, r):
    cumulative = 0
    total = 0
    for i in range(r):
        if i < k:
            cumulative += eigenValueSquare[i]
        total += eigenValueSquare[i]

def SVD_Decomposition(A, tolerance = 1e-15, maxIterations=6767):
    """
    Applies the SVD method in A, (m,n) matrix, if m >= n

    Returns a tuple (U, Sigma, V.t)
    Sigma is an array with singular values
    """

    # ATA is a symetric matrix
    ATA = A.T @ A

    eigenValueSquare, eigenVectors = Jacobi_Decomposition(ATA, tolerance, maxIterations)
    
    eigenValues = np.sqrt(np.maximum(eigenValueSquare, 0.))

    eigenValues, eigenVectors = Sort_By_Eigenvalue_Desc(eigenValues, eigenVectors)

    rank = Compute_Rank(eigenValues, tolerance)

    if not Valid_Rank(rank): return None
    
    # Select the rank main components
    sigma = eigenValues[:rank]
    V = eigenVectors[:, :rank]

    U = Compute_U_From_SVD_Components(A, sigma, V, A.shape[0], rank)

    return U, sigma, V.T

