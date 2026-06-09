# Jacó, filho de Isaac, filho de Abraão, teve 12 filhos.
import numpy as np
import numpy.typing as npt

# find maximum value in symetric matrix aside from the diagonal
def Find_Max_Symetric(A: npt.NDArray[np.float64]) -> tuple[np.float64, int, int]:
    max = abs(A[0][1])
    p: int = 0
    q: int = 1
    m: int = A.shape[0]

    # index: int = 0
    # for row in A[0:(A.shape[0] - 1)]:
    #     j = np.abs(row[index+1:]).argmax() + index + 1
    #     wow = abs(row[j])
    #     if max < wow:
    #         max = wow
    #         q = int(j)
    #         p = index

    #     index = index + 1
    
    for i in range(m):
       for j in range(m):
           if(i != j): 
               if max < abs(A[i][j]):
                   max = abs(A[i][j])
                   p = i
                   q = j

    return (max, p, q)
#end

# calculate the cos and sin(phi) to rotate the matrix A in a way that A[p][q] == 0
def Calculate_Trigonometric(A: npt.NDArray[np.float64], p: int, q: int) -> tuple[float, float]:
    big_phi = (A[q][q] - A[p][p]) / (2 * A[p][q])
    tang = 1
    if abs(big_phi) > 1e-15:
        tang = 1 / (big_phi + np.sign(big_phi) * np.sqrt((big_phi ** 2) + 1))

    cosi = 1 / ((tang ** 2) + 1)
    sino = tang * cosi
        
    return (cosi, sino)


# A needs to be symetric
def Jacobi_Decomposition(A: npt.NDArray[np.float64], tol = 1e-15, kmax = 1000) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    # U is the rotation matrix
    U = np.identity(A.shape[0])
    # V is the product of all rotation matrices
    V = np.identity(A.shape[0])
    # Ak is the k-th iteration of A, approximately a diagonal matrix
    Ak = np.copy(A)
    k = 0

    (max, p, q) = Find_Max_Symetric(A)
    while max > tol and k < kmax:
        # cos(phi) and sin(phi)
        (c, s) = Calculate_Trigonometric(Ak, p, q)

        # construct matrix U from the identity
        U[p][p] = c
        U[p][q] = s
        U[q][p] = -s
        U[q][q] = c

        # V is the product of all rotation matrices
        V = V @ U
        # calculate the roation Vt*A*V
        Ak = V.T @ A @ V

        # revert U to the identity matrix
        U[p][p] = 1
        U[p][q] = 0
        U[q][p] = 0
        U[q][q] = 1

        # next iteration
        (max, p, q) = Find_Max_Symetric(Ak)
        k = k + 1

    return (np.diag(Ak), V)
#end
