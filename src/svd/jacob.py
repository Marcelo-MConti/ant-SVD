# Jacó, filho de Isaac, filho de Abraão, teve 12 filhos.
import numpy as np
import numpy.typing as npt

# find maximum value in symetric matrix
def Find_Max_Symetric(A: npt.NDArray[np.float64]) -> tuple[np.float64, int, int]:
    max: np.float64 = A[0][0]
    index = 0
    p: int = 0
    q: int = 0

    #np.nditer(A, flags=["external_loop"], order='C')
    print(A)
    for row in A:
        j = np.abs(row[index:]).argmax() + index
        wow = abs(row[j])
        if max < wow:
            max = wow
            q = int(j)
            p = index

        index = index + 1
    return (max, p, q)
#end

# calculate the cos and sin(phi) to rotate the matrix A in a way that A[p][q] == 0
def Calculate_Trigonometric(A: npt.NDArray[np.float64], p: int, q: int) -> tuple[int, int]:
    big_phi = (A[q][q] - A[p][p]) / (2 * A[p][q])
    tang = 1
    if big_phi > 1e-10:
        tang = 1 / (big_phi + np.sign(big_phi) * np.sqrt(pow(big_phi, 2) + 1))

    cosi = 1 / (pow(tang, 2) + 1)
    sino = tang * cosi
        
    return (cosi, sino)


# A needs to be symetric
def Jacobi_Decomposition(A: npt.NDArray[np.float64], tol = 1e-9) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    # U is the rotation matrix
    U = np.identity(A.shape[0])
    # V is the product of all rotation matrices
    V = np.identity(A.shape[0])
    # Ak is the k-th iteration of A, approximately a diagonal matrix
    Ak = np.identity(A.shape[0])

    (max, p, q) = Find_Max_Symetric(A)
    while max > tol:
        # cos(phi) and sin(phi)
        (c, s) = Calculate_Trigonometric(A, p, q)

        U[p][p] = c
        U[p][q] = s
        U[q][p] = -s
        U[q][q] = c

        # V is the product of all rotation matrices
        V = V.dot(U)
        # calculate the roation Vt*A*V
        Ak = V.T.dot(A.dot(V))

        # revert U to the identity matrix
        U[p][p] = 0
        U[p][q] = 0
        U[q][p] = 0
        U[q][q] = 0
        (max, p, q) = Find_Max_Symetric(Ak)

    return (Ak, V)
#end


