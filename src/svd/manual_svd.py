import numpy as np
from jacob import Jacobi_Decomposition

def Sort_by_eigenvalue_desc(eigenValues, eigenVectors):
    idx = np.argsort(eigenValues)[::-1]
    eigenValues = eigenValues[idx]
    eigenVectors = eigenVectors[:, idx]
    return eigenValues, eigenVectors 

def Compute_rank(eigenValues, tolerance=1e-10):
    rank = 0
    for k in range(len(eigenValues)):
        if eigenValues[k] > tolerance:
            rank += 1
    return rank

def Valid_rank(rank):
    return rank > 0

def Compute_U_from_svd_components(A, sigma, V, m, rank):
    U = np.zeros((m, rank))
    for i in range(rank):
        U[:,i] = (A @ V[:,i])/sigma[i]
    return U

# Decomposição SVD 
#  A = U*sigma*(V.t)
#  entrada:
#  A = matriz (m, n), m >= n 
#  saída: 
#  U =
#  Sigma =
#  V.t = 
def SVD_decomposition(A, tolerance = 1e-15, maxIterations=6767):

    ATA = A.T @ A

    eigenValueSquare, eigenVectors = Jacobi_Decomposition(ATA, tolerance, maxIterations)
    
    eigenValues = np.sqrt(np.maximum(eigenValueSquare, 0.))

    # Ordenar autoVetores respectivamente com seus autoValores
    eigenValues, eigenVectors = Sort_by_eigenvalue_desc(eigenValues, eigenVectors)

    rank = Compute_rank(eigenValues, tolerance)

    if not Valid_rank(rank): return None

    # seleção dos rank componentes principais
    sigma = eigenValues[:rank]
    V = eigenVectors[:,:rank]

    # Criar a matriz U
    U = Compute_U_from_svd_components(A, sigma, V, A.shape[0], rank)

    return U, sigma, V.T

def Cumulative_variance(eigenValueSquare, k, r):
    cumulative = 0
    total = 0
    for i in range(r):
        if(i<k):
            cumulative += eigenValueSquare[i]
        total += eigenValueSquare[i]
    
    return cumulative/total
