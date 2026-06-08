# Jacó, filho de Isaac, filho de Abraão, teve 12 filhos.
import numpy as np
import numpy.typing as npt

def Find_Max_Symetric(A: npt.NDArray[np.float64]) -> tuple[np.float64, int, int]:
    # find maximum value in symetric matrix
    max: np.float64 = A[0][0]
    index = 0
    p: int = 0
    q: int = 0

    #np.nditer(A, flags=["external_loop"], order='C')
    print(A)
    for row in A:
        j = row[index:].argmax()
        wow = abs(row[j])
        if max < wow:
            max = wow
            q = int(j)
            p = index

        index = index + 1
    return (max, p, q)


# A needs to be symetric
def Jacobi_Decomposition(A: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    (max, p, q) = Find_Max_Symetric(A)

    return A
#end


Jacobi_Decomposition(np.array([[1, 2, 3], [4, 5, 6]]))
