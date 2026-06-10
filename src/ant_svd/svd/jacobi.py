from math import sqrt
import numpy as np
import numpy.typing as npt


def Find_Max_Symmetric(A: npt.NDArray[np.float64]) -> tuple[np.float64, int, int]:
    """
    Finds the maximal entry in absolute value for a symmetric matrix,
    ignoring its diagonal.

    Returns a tuple with the element's absolute value,
    row and column indexes.
    """
    max = abs(A[0][1])
    p: int = 0
    q: int = 1

    # Iterate through all the rows of the matrix.
    # Because A is symmetric, we only need to look the elements
    # above or below the diagonal. Here, we are inspecting the
    # lower triangular matrix.
    for (i, row) in enumerate(A):
        for (j, element) in enumerate(row[0:i]):
            if max < abs(element):
                # found new maximum absolute value
                max = abs(element)
                p = i
                q = j

    return (max, p, q)


def Calculate_Trigonometric(A: npt.NDArray[np.float64], p: int, q: int) -> tuple[float, float]:
    """
    Calculates the value for cos(phi) and sin(phi) such that a (p, q)-rotation by phi
    applied on A will zero out the element A[p][q].

    Returns a tuple of (cos(phi), sin(phi)).
    """

    # These equations are derived from Ut A U
    phi = (A[q][q] - A[p][p]) / (2 * A[p][q])
    tang = 1
    if abs(phi) > 1e-15:
        tang = 1 / (phi + np.sign(phi) * sqrt((phi ** 2) + 1))

    cosx = 1 / np.sqrt((tang ** 2) + 1)
    sinx = tang * cosx

    return (cosx, sinx)


def Jacobi_Decomposition(A: npt.NDArray[np.float64], tol = 1e-15, kmax = 1000) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """
    Applies the Jacobi iterative method to extract the eigenvalues and eigenvectors of the matrix A

    A needs to be symmetric. The following stopping conditions are used:
      - maximum element in absolute value of Ak (iteration matrix), ignoring the diagonal 
      - number of iterations
      
    Returns a tuple where the first entry is an array of eigenvalues and the second entry
    is a matrix that stores the eigenvectors as column vectors.
    """

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
