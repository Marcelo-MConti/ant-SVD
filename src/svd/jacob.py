import numpy as np
import numpy.typing as npt


# Find maximum value in symmetric matrix aside from the diagonal
# Return (absolute of the biggest value, its line and column indexes)
def Find_Max_Symmetric(A: npt.NDArray[np.float64]) -> tuple[np.float64, int, int]:
    max = abs(A[0][1])
    p: int = 0
    q: int = 1
    m: int = A.shape[0]

    for i in range(m):
       for j in range(m):
           if i != j:
               if max < abs(A[i][j]):
                   max = abs(A[i][j])
                   p = i
                   q = j

    return (max, p, q)


# Calculate the cosine and sine to rotate the matrix A in a way that A[p][q] == 0
# Return their values
def Calculate_Trigonometric(A: npt.NDArray[np.float64], p: int, q: int) -> tuple[float, float]:
    # These equations are derived from Ut A U
    phi = (A[q][q] - A[p][p]) / (2 * A[p][q])
    tang = 1
    if abs(phi) > 1e-15:
        tang = 1 / (phi + np.sign(phi) * np.sqrt((phi ** 2) + 1))

    cosx = 1 / np.sqrt((tang ** 2) + 1)
    sinx = tang * cosx
        
    return (cosx, sinx)


# Apply the Jacobi iterative method to extract the eigenvalues and eigenvectors of the matrix A
# A needs to be symetric. There are two stopping conditions being used.
# Thy are: maximum value outside the diagonal in the Ak matrix and number of iterations.
# Return (array of the eigenvalues, matrix of the eigenvectors)
def Jacobi_Decomposition(A: npt.NDArray[np.float64], tol = 1e-15, kmax = 1000) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    # U is the rotation matrix
    U = np.identity(A.shape[0])

    # V is the product of all rotation matrices
    V = np.identity(A.shape[0])

    # Ak is the k-th iteration of A, approximating a diagonal matrix
    Ak = np.copy(A)
    k = 0

    (max, p, q) = Find_Max_Symmetric(A)
    while max > tol and k < kmax:
        # cos(phi) and sin(phi)
        (c, s) = Calculate_Trigonometric(Ak, p, q)

        # construct matrix U from the identity
        U[p][p] =  c
        U[p][q] =  s
        U[q][p] = -s
        U[q][q] =  c

        # V is the product of all rotation matrices
        V = V @ U

        # calculate the rotation Vt*A*V
        Ak = V.T @ A @ V

        # revert U to the identity matrix
        U[p][p] = 1
        U[p][q] = 0
        U[q][p] = 0
        U[q][q] = 1

        # next iteration
        (max, p, q) = Find_Max_Symmetric(Ak)
        k = k + 1

    return (np.diag(Ak), V)
